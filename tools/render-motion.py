#!/usr/bin/env python3
"""Render the device-mockup films in tools/motion/scenes.html to MP4.

Each frame is posed with the page's render(t), captured over DevTools (the same
driver print-cv.py uses) and piped to ffmpeg, so the video is frame-exact and
loops seamlessly. Frames are captured at 2x (the device scenes) and downscaled with Lanczos, so the
3D-tilted screenshots stay sharp. Writes, per scene, into assets/motion/:

    <scene>.mp4     full size, for wide screens
    <scene>-m.mp4   the phone cut: cropped to the action (if the scene says how) and smaller
    <scene>.jpg     poster, the first frame

    python -m pip install --user imageio-ffmpeg   # or put ffmpeg on PATH
    python tools/render-motion.py                 # all scenes
    python tools/render-motion.py soc chalet      # some of them
"""

import base64
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "motion")
SCENES = ["hero", "platform", "chalet", "soc", "smartcare",
          "flow", "constellation", "bokeh", "blueprint", "trail", "aurora"]
FPS = 30
# x264 for flat UI graphics: high quality, and tuned so gradients don't band
X264 = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation",
        "-pix_fmt", "yuv420p", "-color_range", "tv", "-movflags", "+faststart", "-an"]

spec = importlib.util.spec_from_file_location("printcv", os.path.join(HERE, "print-cv.py"))
printcv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(printcv)


def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    return shutil.which("ffmpeg") or sys.exit("ffmpeg not found: pip install imageio-ffmpeg")


def run(ffmpeg, args):
    res = subprocess.run([ffmpeg, "-y", "-loglevel", "error"] + args)
    if res.returncode != 0:
        sys.exit("ffmpeg failed: " + " ".join(args))


def main():
    names = sys.argv[1:] or SCENES
    unknown = [n for n in names if n not in SCENES]
    if unknown:
        sys.exit("unknown scene(s): " + ", ".join(unknown))
    ffmpeg = find_ffmpeg()
    os.makedirs(OUT, exist_ok=True)

    httpd, port = printcv.serve(ROOT)
    profile = tempfile.mkdtemp(prefix="motion-")
    dbg = 9335
    proc = subprocess.Popen(
        [
            printcv.find_chrome(), "--headless=new", "--no-first-run", "--hide-scrollbars",
            f"--remote-debugging-port={dbg}", f"--user-data-dir={profile}", "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ws = printcv.WS(printcv.devtools_url(dbg))
        state = {"id": 0}

        def call(method, **params):
            state["id"] += 1
            ws.send({"id": state["id"], "method": method, "params": params})
            while True:
                res = ws.recv()
                if res.get("id") == state["id"]:
                    if "error" in res:
                        raise RuntimeError(f"{method}: {res['error']}")
                    return res.get("result", {})

        def evaluate(expr):
            res = call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
            if "exceptionDetails" in res:
                raise RuntimeError(f"{expr}: {res['exceptionDetails']}")
            return res["result"].get("value")

        call("Page.enable")
        for name in names:
            call("Page.navigate", url=f"http://127.0.0.1:{port}/tools/motion/scenes.html?s={name}")
            deadline = time.time() + 30
            while time.time() < deadline:
                if ws.recv().get("method") == "Page.loadEventFired":
                    break
            info = evaluate("window.ready.then(() => window.SCENE)")
            w, h, T = info["w"], info["h"], info["T"]
            # frames are captured at ss x and scaled down; the page reloads at that
            # pixel ratio so canvases are sized for it
            ss = info.get("ss", 2)
            call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=ss, mobile=False)
            call("Page.reload")
            deadline = time.time() + 30
            while time.time() < deadline:
                if ws.recv().get("method") == "Page.loadEventFired":
                    break
            evaluate("window.ready")

            mp4 = os.path.join(OUT, f"{name}.mp4")
            enc = subprocess.Popen(
                [
                    ffmpeg, "-y", "-loglevel", "error",
                    "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                    "-vf", f"scale={w}:{h}:flags=lanczos:out_range=tv",
                    "-crf", str(info.get("crf", 20)),
                ] + X264 + [mp4],
                stdin=subprocess.PIPE,
            )
            frames = int(T * FPS)
            for i in range(frames):
                evaluate(f"render({i / FPS})")
                shot = call("Page.captureScreenshot", format="jpeg", quality=98)
                enc.stdin.write(base64.b64decode(shot["data"]))
            enc.stdin.close()
            if enc.wait() != 0:
                sys.exit(f"ffmpeg failed on {name}")

            # poster: the first frame, as the browser will show it before play
            run(ffmpeg, ["-i", mp4, "-frames:v", "1", "-q:v", "3", os.path.join(OUT, f"{name}.jpg")])

            # the phone cut: crop (fractions of the frame) then scale to the phone width
            m = info.get("mobile", {})
            x0, y0, x1, y1 = m.get("crop", [0, 0, 1, 1])
            cw, ch = round((x1 - x0) * w / 2) * 2, round((y1 - y0) * h / 2) * 2
            mw = m.get("w", 960)
            mh = round(mw * ch / cw / 2) * 2
            mob = os.path.join(OUT, f"{name}-m.mp4")
            run(ffmpeg, ["-i", mp4, "-vf",
                         f"crop={cw}:{ch}:{round(x0 * w)}:{round(y0 * h)},scale={mw}:{mh}:flags=lanczos",
                         "-crf", "23"] + X264 + [mob])

            kb = lambda p: os.path.getsize(p) // 1024
            print(f"{name}: {w}x{h} {T}s {kb(mp4)} KB  |  phone {mw}x{mh} {kb(mob)} KB")
        ws.close()
    finally:
        proc.terminate()
        httpd.shutdown()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()

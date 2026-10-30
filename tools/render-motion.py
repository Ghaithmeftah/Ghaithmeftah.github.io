#!/usr/bin/env python3
"""Render the device-mockup loops in tools/motion/scenes.html to MP4.

Each frame is posed with the page's render(t), captured over DevTools (the same
driver print-cv.py uses) and piped to ffmpeg, so the video is frame-exact and
loops seamlessly. Writes assets/motion/<scene>.mp4 and a <scene>.jpg poster.

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
SCENES = ["showreel", "chalet", "soc", "smartcare"]
FPS = 30

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
            call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
            evaluate("window.ready")

            mp4 = os.path.join(OUT, f"{name}.mp4")
            enc = subprocess.Popen(
                [
                    ffmpeg, "-y", "-loglevel", "error",
                    "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-an", mp4,
                ],
                stdin=subprocess.PIPE,
            )
            frames = int(T * FPS)
            for i in range(frames):
                evaluate(f"render({i / FPS})")
                shot = call("Page.captureScreenshot", format="jpeg", quality=94)
                data = base64.b64decode(shot["data"])
                enc.stdin.write(data)
                if i == 0:
                    with open(os.path.join(OUT, f"{name}.jpg"), "wb") as f:
                        f.write(data)
            enc.stdin.close()
            if enc.wait() != 0:
                sys.exit(f"ffmpeg failed on {name}")
            print(f"{os.path.relpath(mp4, ROOT)}  {w}x{h}  {T}s  {os.path.getsize(mp4) // 1024} KB")
        ws.close()
    finally:
        proc.terminate()
        httpd.shutdown()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()

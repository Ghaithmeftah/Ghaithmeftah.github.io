#!/usr/bin/env python3
"""Screenshot a page of this site, optionally scrolled to a selector.

Chrome's --screenshot flag shoots before a hash link has scrolled, so this drives
the same DevTools session print-cv.py uses and scrolls first.

    python tools/shot.py index.html out.png                 # top of the page
    python tools/shot.py index.html out.png --at "#hire"    # scrolled to a section
    python tools/shot.py index.html out.png --w 390 --h 844 # phone-sized
"""

import argparse
import base64
import importlib.util
import os
import shutil
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location("printcv", os.path.join(HERE, "print-cv.py"))
printcv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(printcv)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("out")
    ap.add_argument("--at", default=None, help="CSS selector to scroll to")
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=900)
    ap.add_argument("--full", action="store_true", help="capture the whole page height")
    ap.add_argument("--wait", type=int, default=700, help="ms to wait after scrolling, for animations")
    args = ap.parse_args()

    httpd, port = printcv.serve(ROOT)
    profile = tempfile.mkdtemp(prefix="shot-")
    dbg = 9334
    proc = subprocess.Popen(
        [
            printcv.find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run",
            "--hide-scrollbars", f"--window-size={args.w},{args.h}",
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

        call("Page.enable")
        call("Emulation.setDeviceMetricsOverride",
             width=args.w, height=args.h, deviceScaleFactor=1, mobile=args.w < 700)
        call("Page.navigate", url=f"http://127.0.0.1:{port}/{args.page}")
        deadline = time.time() + 30
        while time.time() < deadline:
            if ws.recv().get("method") == "Page.loadEventFired":
                break
        call("Runtime.evaluate",
             expression="document.fonts.ready.then(() => new Promise(r => setTimeout(r, 800)))",
             awaitPromise=True)

        if args.at:
            call("Runtime.evaluate", expression=f"""
                (() => {{
                  document.documentElement.style.scrollBehavior = 'auto';
                  const t = document.querySelector({args.at!r});
                  if (!t) return 'selector not found';
                  window.scrollTo(0, t.getBoundingClientRect().top + window.scrollY - 24);
                  return 'ok';
                }})()""")
            call("Runtime.evaluate",
                 expression=f"new Promise(r => setTimeout(r, {args.wait}))", awaitPromise=True)

        params = {"format": "png"}
        if args.full:
            params["captureBeyondViewport"] = True
        shot = call("Page.captureScreenshot", **params)
        dest = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        with open(dest, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print(dest)
        ws.close()
    finally:
        proc.terminate()
        httpd.shutdown()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()

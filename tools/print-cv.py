#!/usr/bin/env python3
"""Render the web CV sheet, cv.html (and fr/cv.html), to A4 PDFs for proofing.

The PDFs the site links to are no longer made here: they are the ATS resumes in
tools/resume/, built by tools/build-resumes.py. This script writes to tools/out/ so
it can never overwrite them. shot.py still imports its DevTools helpers.

Chrome's `--print-to-pdf` flag ignores `@page { margin: 0 }` and silently adds its
own margins, which pushed this one-page CV onto a second sheet. Driving Chrome over
the DevTools protocol instead lets us set the paper size and zero margins explicitly,
so the PDF matches the page.

    python tools/print-cv.py            # serves the folder itself and writes both PDFs
    python tools/print-cv.py --keep     # leave Chrome's user-data dir for debugging
"""

import base64
import functools
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    ("cv.html", "tools/out/cv-sheet-EN.pdf"),
    ("fr/cv.html", "tools/out/cv-sheet-FR.pdf"),
]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

A4_W_IN, A4_H_IN = 8.27, 11.69


# ---------------------------------------------------------------- tiny ws client
class WS:
    """Minimal RFC 6455 client — enough for one DevTools session."""

    def __init__(self, url):
        _, rest = url.split("://", 1)
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(
            (
                f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
                f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            ).encode()
        )
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, payload: dict):
        data = json.dumps(payload).encode()
        head = bytes([0x81])
        n = len(data)
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 1 << 16:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(head + mask + masked)

    def recv(self):
        frame = b""
        while True:
            b0, b1 = self._read(2)
            fin, ln = b0 & 0x80, b1 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._read(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._read(8))[0]
            frame += self._read(ln)
            if fin:
                return json.loads(frame.decode())

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


# ------------------------------------------------------------------- local serve
def serve(root):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    handler.log_message = lambda *a, **k: None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def find_chrome():
    for path in CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    sys.exit("No Chrome or Edge binary found — edit CHROME_CANDIDATES in this script.")


def devtools_url(port, tries=60):
    for _ in range(tries):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as r:
                for target in json.load(r):
                    if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
                        return target["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.4)
    sys.exit("Chrome never exposed a DevTools page target.")


def main():
    keep = "--keep" in sys.argv
    httpd, port = serve(ROOT)
    chrome = find_chrome()
    profile = tempfile.mkdtemp(prefix="cvprint-")
    dbg = 9333

    proc = subprocess.Popen(
        [
            chrome, "--headless=new", "--disable-gpu", "--no-first-run",
            f"--remote-debugging-port={dbg}", f"--user-data-dir={profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    try:
        ws = WS(devtools_url(dbg))
        msg_id = 0

        def call(method, **params):
            nonlocal msg_id
            msg_id += 1
            ws.send({"id": msg_id, "method": method, "params": params})
            while True:
                res = ws.recv()
                if res.get("id") == msg_id:
                    if "error" in res:
                        raise RuntimeError(f"{method}: {res['error']}")
                    return res.get("result", {})

        call("Page.enable")
        call("Runtime.enable")

        for src, out in PAGES:
            if not os.path.exists(os.path.join(ROOT, src)):
                print(f"skip {src} (not present yet)")
                continue
            call("Page.navigate", url=f"http://127.0.0.1:{port}/{src}")
            # wait for the load event, then for the web fonts to be applied
            deadline = time.time() + 30
            while time.time() < deadline:
                ev = ws.recv()
                if ev.get("method") == "Page.loadEventFired":
                    break
            call(
                "Runtime.evaluate",
                expression="document.fonts.ready.then(() => new Promise(r => setTimeout(r, 300)))",
                awaitPromise=True,
            )
            result = call(
                "Page.printToPDF",
                printBackground=True,
                paperWidth=A4_W_IN,
                paperHeight=A4_H_IN,
                marginTop=0, marginBottom=0, marginLeft=0, marginRight=0,
                preferCSSPageSize=False,
                scale=1,
            )
            data = base64.b64decode(result["data"])
            dest = os.path.join(ROOT, out)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            pages = data.count(b"/Type /Page\n")
            flag = "" if pages == 1 else f"  <-- {pages} pages, tighten the sheet"
            print(f"{out}  {len(data) // 1024} KB  {pages} page(s){flag}")

        ws.close()
    finally:
        proc.terminate()
        httpd.shutdown()
        if not keep:
            shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()

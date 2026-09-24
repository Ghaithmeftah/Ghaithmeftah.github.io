#!/usr/bin/env python3
"""Render the four ATS resumes in tools/resume/ to the PDFs the site links to.

These are the recruiter-facing CVs: single column, no ligatures, real text links,
one A4 page each. The English pages link the -EN files and the French mirror links
the -FR files, so a reader always downloads the CV in the language they are reading.

    python tools/build-resumes.py

Each resume carries its own @page margins, so Chrome's plain --print-to-pdf is
enough here (the margin problem noted in the old print-cv.py only bit a sheet that
asked for zero margins).
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "resume")

JOBS = [
    ("fullstack-en.html", "Ghaith-Mefteh-CV-EN.pdf"),
    ("mobile-en.html", "Ghaith-Mefteh-CV-Mobile-EN.pdf"),
    ("fullstack-fr.html", "Ghaith-Mefteh-CV-FR.pdf"),
    ("mobile-fr.html", "Ghaith-Mefteh-CV-Mobile-FR.pdf"),
]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    found = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
    if not found:
        sys.exit("build-resumes: no Chrome or Edge found")
    return found


def page_count(pdf):
    # count page objects without a PDF library: good enough for a one-page check
    data = open(pdf, "rb").read()
    return data.count(b"/Type /Page") - data.count(b"/Type /Pages")


def main():
    chrome = find_chrome()
    failed = False
    for src, out in JOBS:
        src_path = os.path.join(SRC, src)
        out_path = os.path.join(ROOT, "assets", out)
        url = "file:///" + src_path.replace("\\", "/").replace(" ", "%20")
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             "--print-to-pdf=" + out_path, url],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        pages = page_count(out_path)
        flag = "" if pages == 1 else "  <-- not one page"
        failed |= pages != 1
        print(f"{out}: {pages} page(s){flag}")
    if failed:
        sys.exit("build-resumes: a resume spilled past one page")


if __name__ == "__main__":
    main()

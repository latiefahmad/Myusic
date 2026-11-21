#!/usr/bin/env python3
"""Collapse the duplicated-prefix artefacts from running the token rebrand
more than once: any run of z/Z before myusic/Myusic/MYUSIC becomes one.

    zzzmyusic -> zmyusic      ZZZZMyusic -> ZMyusic      ZZMYUSIC -> ZMYUSIC

Run from the repo root: py branding/fix_prefixes.py
"""
from __future__ import annotations

import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAT = re.compile(r"[zZ]+(?=myusic|Myusic|MYUSIC)")
# Also the fully-cased forms already replaced once, e.g. ZZMyusic etc.
PAT2 = re.compile(r"[zZ]{2,}(?=myusic|Myusic|MYUSIC)")

EXTS = {
    "kt", "kts", "java", "swift", "xml", "ts", "tsx", "md", "cpp", "h", "hpp",
    "cc", "sh", "yml", "yaml", "go", "json", "html", "txt", "mjs", "js", "css",
    "svg", "py", "plist", "entitlements", "xcscheme", "xcworkspacedata",
    "pbxproj", "xcstrings", "xctestplan", "example", "pro", "mod", "map",
    "editorconfig", "service", "gitignore", "gitattributes", "gradle",
    "properties", "toml",
}


def fix(text: str) -> str:
    # collapse the run, preserving the case of the FIRST z/Z
    def repl(m):
        return m.group(0)[0]
    return PAT.sub(repl, text)


def main():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    changed = 0
    for rel in files:
        if rel.startswith("branding/"):
            continue
        ext = os.path.splitext(rel)[1].lstrip(".").lower()
        if ext not in EXTS:
            continue
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            raw = f.read()
        if b"\x00" in raw:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        new = fix(text)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            changed += 1
    print("files fixed:", changed)


if __name__ == "__main__":
    main()

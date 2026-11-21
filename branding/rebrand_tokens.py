#!/usr/bin/env python3
"""Token rebrand: Myusic/myusic/MYUSIC -> ZMyusic/zmyusic/ZMYUSIC.

Walks every git-tracked text file (skipping branding/ and binaries) and applies
the ordered replacements. Run from the repo root:

    py branding/rebrand_tokens.py
"""
from __future__ import annotations

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTS = {
    "kt", "kts", "java", "swift", "xml", "ts", "tsx", "md", "cpp", "h", "hpp",
    "cc", "sh", "yml", "yaml", "go", "json", "html", "txt", "mjs", "js", "css",
    "svg", "py", "plist", "entitlements", "xcscheme", "xcworkspacedata",
    "pbxproj", "xcstrings", "xctestplan", "example", "pro", "mod", "map",
    "editorconfig", "service", "gitignore", "gitattributes", "gradle",
    "properties", "toml", "xcworkspacedata",
}

REPL = [
    ("com.music.myusic", "com.zmyusic.zmyusic"),
    ("com.dev.myusic", "com.dev.zmyusic"),
    ("com/music/myusic", "com/zmyusic/zmyusic"),
    ("com/dev/myusic", "com/dev/zmyusic"),
    ("Java_com_music_myusic", "Java_com_zmyusic_zmyusic"),
    ("MyusicApplication", "ZMyusicApplication"),
    ("MyusicKit", "ZMyusicKit"),
    ("MyusicCore", "ZMyusicCore"),
    ("MyusicTestSupport", "ZMyusicTestSupport"),
    ("Myusic", "ZMyusic"),
    ("MYUSIC", "ZMYUSIC"),
    ("myusic", "zmyusic"),
]


def main():
    files = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()

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
            continue  # binary
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for a, b in REPL:
            new = new.replace(a, b)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            changed += 1
    print("files changed:", changed)


if __name__ == "__main__":
    main()

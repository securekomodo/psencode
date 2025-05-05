#!/usr/bin/env python3
"""psencode.py – Tiny PowerShell encode↔decode helper.

* **Encode** → UTF‑16‑LE Base64 for `-EncodedCommand` (default when reading **stdin** and no flag given)
* **Decode** ← same format back to plain text (requires `-d/--decode`)
* Input accepted from positional text, `-f FILE`, or **stdin** without flags.

Quick examples
==============
    # Encode from literal string
    ./psencode.py -e "Get-Process | Out-String"

    # Encode by piping a file (no -e needed)
    cat script.ps1 | ./psencode.py > payload.b64

    # Decode a blob back to text
    ./psencode.py -d "SQBtACAAZQB4..." > script.ps1
"""
from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

__all__ = ["encode_ps", "decode_ps"]

# ──────────────────────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────────────────────

def encode_ps(text: str) -> str:
    """Return UTF‑16‑LE → Base64 (ASCII) **without newlines**."""
    return base64.b64encode(text.encode("utf-16le")).decode()


def decode_ps(b64: str) -> str:
    """Reverse of :pyfunc:`encode_ps` (tolerates surrounding whitespace)."""
    return base64.b64decode(b64.strip()).decode("utf-16le")

# ──────────────────────────────────────────────────────────────────────────────
# I/O helpers
# ──────────────────────────────────────────────────────────────────────────────

def _read_source(args: argparse.Namespace) -> str:
    """Fetch PowerShell code from file, positional, or stdin."""
    if args.file:
        try:
            return Path(args.file).read_text(encoding="utf-8")
        except Exception as exc:
            sys.exit(f"[!] cannot read {args.file}: {exc}")

    if args.source:
        return " ".join(args.source)

    if not sys.stdin.isatty():
        return sys.stdin.read()

    sys.exit("[!] No input provided – supply text, -f FILE, or pipe via stdin.")


def _write_output(data: str, dest: str | None):
    if dest:
        try:
            Path(dest).write_text(data, encoding="utf-8")
        except Exception as exc:
            sys.exit(f"[!] cannot write {dest}: {exc}")
    else:
        print(data, end="")  # no newline for easy clipboard use

# ──────────────────────────────────────────────────────────────────────────────
# CLI wiring
# ──────────────────────────────────────────────────────────────────────────────

def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="psencode",
        description="Encode/decode the UTF‑16LE Base64 blobs used by PowerShell -EncodedCommand.",
    )

    action = p.add_mutually_exclusive_group(required=False)
    action.add_argument("-e", "--encode", action="store_true", help="Force encode text → UTF‑16LE Base64")
    action.add_argument("-d", "--decode", action="store_true", help="Decode UTF‑16LE Base64 → text")

    p.add_argument("source", nargs=argparse.REMAINDER, help="PowerShell text (omit to read from stdin)")
    p.add_argument("-f", "--file", metavar="PATH", help="Read PowerShell text from file")
    p.add_argument("-o", "--output", metavar="PATH", help="Write result to file instead of stdout")

    return p


def cli(argv: list[str] | None = None):
    args = _make_parser().parse_args(argv)

    raw = _read_source(args)

    # Determine action: decode flag wins; otherwise encode by default
    if args.decode:
        result = decode_ps(raw)
    else:
        result = encode_ps(raw)

    _write_output(result, args.output)

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()

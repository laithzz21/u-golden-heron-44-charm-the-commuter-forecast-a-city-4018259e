#!/usr/bin/env python3
"""Entry for make.fun bounty: charm the commuter — a one-line weather
forecast for a city that does not exist.

Prints the single-line forecast to stdout and also writes it to the output
directory (``/output/entry.txt`` by default, or ``$MAKEFUN_OUTPUT`` when
set), verifying the written file by reading it back.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import re
import sys

ENTRY = (
    "Frogsbottom: 14°C, light drizzle of confetti, and a 90% chance the "
    "8:04 bus is actually on time — pack an umbrella and a little hope."
)


MAX_CHARS = 140


def validate(text: str) -> None:
    """The entry must be a single line of at most 140 characters, naming
    the invented city before a colon and giving it weather (a °C reading)."""
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry must be 1-{MAX_CHARS} characters, got {len(text)}")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    city, _, forecast = text.partition(": ")
    if not city or not city.replace(" ", "").isalpha() or not forecast:
        raise ValueError("entry must name the city, then the forecast after ': '")
    if "°C" not in forecast:
        raise ValueError("entry must give the city weather (a °C reading)")
    # A commuter anchor: the forecast must mention a departure time, so the
    # bored commuter the bounty is aimed at is actually in the line.
    if not re.search(r"\b\d{1,2}:\d{2}\b", forecast):
        raise ValueError("entry must mention a bus/train time for the commuter")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    print(ENTRY, flush=True)
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY:
            raise RuntimeError("verification failed: written entry does not match")
    except OSError as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

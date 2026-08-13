#!/usr/bin/env python3
"""Estimate Chinese dialogue duration for storyboard planning.

This helper is intentionally conservative and does not replace a human check of
how numbers, Latin text, abbreviations, ellipses, and performance pauses are read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys


PAUSE_RANGES = {
    ",": (0.10, 0.20),
    "，": (0.10, 0.20),
    ";": (0.15, 0.25),
    "；": (0.15, 0.25),
    ".": (0.20, 0.35),
    "。": (0.20, 0.35),
    "?": (0.20, 0.35),
    "？": (0.20, 0.35),
    "!": (0.20, 0.35),
    "！": (0.20, 0.35),
}


def estimate(text: str, cps: float, tail: float, pause_mode: str) -> dict[str, float | int | str]:
    if cps <= 0:
        raise ValueError("cps must be greater than zero")
    pause_index = {"low": 0, "mid": None, "high": 1}[pause_mode]
    pause = 0.0
    for char in text:
        if char in PAUSE_RANGES:
            low, high = PAUSE_RANGES[char]
            pause += (low + high) / 2 if pause_index is None else (low, high)[pause_index]
    stripped = re.sub(r"[\s,，;；.。?？!！:：、…—\-\"“”'‘’（）()【】\[\]]", "", text)
    units = len(stripped)
    speech = units / cps
    total = speech + pause + tail
    return {
        "text": text,
        "effective_units": units,
        "characters_per_second": cps,
        "speech_seconds": round(speech, 2),
        "punctuation_pause_seconds": round(pause, 2),
        "tail_seconds": round(tail, 2),
        "estimated_total_seconds": round(total, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate dialogue duration for 10-second AI storyboards.")
    parser.add_argument("text", nargs="?", help="Dialogue text; reads stdin when omitted.")
    parser.add_argument("--cps", type=float, default=5.0, help="Effective pronunciation units per second.")
    parser.add_argument("--tail", type=float, default=0.2, help="Lip-sync tail in seconds; use 0 for inner monologue.")
    parser.add_argument("--pause", choices=("low", "mid", "high"), default="mid", help="Punctuation pause estimate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()
    text = args.text if args.text is not None else sys.stdin.read().strip()
    if not text:
        parser.error("dialogue text is required")
    result = estimate(text, args.cps, args.tail, args.pause)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

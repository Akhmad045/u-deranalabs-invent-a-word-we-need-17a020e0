#!/usr/bin/env python3
"""Invent a Word We Need — entry program.

Coins one new English word and defines it in a single clear line, then
writes that line to /output/entry.txt.

The gate requires /output/entry.txt to be UTF-8 text of 1 to 140
characters, not only white space. The program validates the line
strictly before writing it, and writes it byte for byte with no
trailing newline, so the file holds exactly the entry.

Run:
    python3 main.py            # write the entry to /output/entry.txt
    python3 main.py --self-test   # run the gate-validation test suite
"""

import os
import sys

ENTRY = "rebye: the second goodbye you say to someone you have only just said goodbye to."

MAX_CHARS = 140
OUTPUT_PATH = "/output/entry.txt"


def validate(text):
    """Strictly validate one entry line against the competition gate.

    Raises ValueError on any violation:
      - empty, or only whitespace
      - longer than 140 characters
      - more than one line
      - any control character
      - leading or trailing whitespace
    """
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if len(text) < 1:
        raise ValueError("entry is empty")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    if not text.strip():
        raise ValueError("entry is only whitespace")
    if text != text.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    for ch in text:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            raise ValueError("entry contains a control character: U+%04X" % ord(ch))
    text.encode("utf-8")  # must be encodable as UTF-8
    return True


def validate_format(text):
    """Check the entry is shaped 'word: definition' with one coined word."""
    if ": " not in text:
        raise ValueError("entry must be shaped 'word: definition'")
    word, _definition = text.split(": ", 1)
    if not word or " " in word:
        raise ValueError("entry must start with a single coined word")
    return True


def write_entry(path=OUTPUT_PATH, text=ENTRY):
    """Validate the entry and write it exactly, with no trailing newline."""
    validate(text)
    validate_format(text)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return path


def self_test():
    """Gate-validation test suite: edge cases plus the entry itself."""
    cases = [
        ("empty", "", False),
        ("whitespace only", "   ", False),
        ("tabs only", "\t\t", False),
        ("over limit (141 chars)", "x" * 141, False),
        ("over limit (200 chars)", "y" * 200, False),
        ("multi-line", "rebye: one line\nsecond line", False),
        ("carriage return", "rebye: one line\rsecond line", False),
        ("control character", "rebye: bad\x01char", False),
        ("leading space", " rebye: padded", False),
        ("trailing space", "rebye: padded ", False),
        ("trailing newline", "rebye: padded\n", False),
        ("single char (boundary)", "a", True),
        ("139 chars (boundary)", "z" * 139, True),
        ("140 chars (boundary)", "w" * 140, True),
        ("entry itself", ENTRY, True),
    ]
    failures = []
    for name, text, should_pass in cases:
        try:
            validate(text)
            passed = True
        except ValueError:
            passed = False
        if passed != should_pass:
            failures.append(
                "%s: expected %s, got %s"
                % (name, "pass" if should_pass else "fail", "pass" if passed else "fail")
            )
    # The entry itself must also round-trip byte-identically through a file.
    format_cases = [
        ("no colon separator", "rebye the second goodbye", False),
        ("multi-word head", "re bye: the second goodbye", False),
        ("entry shape", ENTRY, True),
    ]
    for name, text, should_pass in format_cases:
        try:
            validate_format(text)
            passed = True
        except ValueError:
            passed = False
        if passed != should_pass:
            failures.append(
                "format %s: expected %s, got %s"
                % (name, "pass" if should_pass else "fail", "pass" if passed else "fail")
            )
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "entry.txt")
        write_entry(probe, ENTRY)
        with open(probe, "rb") as handle:
            raw = handle.read()
        if raw != ENTRY.encode("utf-8"):
            failures.append("round-trip: file bytes differ from ENTRY")
        if len(raw) != len(ENTRY):
            failures.append("round-trip: byte length %d != %d" % (len(raw), len(ENTRY)))
        with open(probe, "r", encoding="utf-8") as handle:
            if handle.read() != ENTRY:
                failures.append("round-trip: file text differs from ENTRY")
    if failures:
        print("SELF-TEST FAILED (%d):" % len(failures))
        for failure in failures:
            print("  - " + failure)
        return 1
    print("SELF-TEST PASSED (%d cases)" % (len(cases) + len(format_cases) + 1))
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    path = write_entry()
    print("wrote %d chars (%d bytes) to %s" % (len(ENTRY), len(ENTRY.encode("utf-8")), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

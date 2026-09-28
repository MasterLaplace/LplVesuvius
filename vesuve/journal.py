"""The journal: one line per event, on standard error, never on standard output.

A line carries a stable CODE (to filter on), `key=value` fields (to aggregate) and the run identifier (to
correlate). The level is set without rebuilding anything: `VESUVE_LOG=DEBUG|INFO|WARN|ERROR` (INFO by default).

⚠ The journal is not a results channel: what a pipeline concludes goes into its `report.json`, and nothing ever
reads these lines back to decide anything.
"""
from __future__ import annotations

import os
import sys
import uuid
from typing import TextIO

LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}


class Journal:
    """An injected journal: the tests hand it a stream, the pipelines the process's own."""

    def __init__(self, stream: TextIO | None = None, level: str | None = None, run: str | None = None):
        self.stream = stream if stream is not None else sys.stderr
        chosen = (level or os.environ.get("VESUVE_LOG", "INFO")).upper()
        if chosen not in LEVELS:
            raise ValueError(f"unknown journal level {chosen!r}: expected one of {sorted(LEVELS)}")
        self.threshold = LEVELS[chosen]
        self.run = run or uuid.uuid4().hex[:8]

    def _write(self, level: str, code: str, fields: dict) -> None:
        if LEVELS[level] < self.threshold:
            return
        parts = [f"{level:<5}", code, f"run={self.run}"]
        for key, value in fields.items():
            text = str(value)
            parts.append(f"{key}={text!r}" if (" " in text or "=" in text or not text) else f"{key}={text}")
        print(" ".join(parts), file=self.stream, flush=True)

    def debug(self, code: str, /, **fields) -> None:
        self._write("DEBUG", code, fields)

    def info(self, code: str, /, **fields) -> None:
        self._write("INFO", code, fields)

    def warn(self, code: str, /, **fields) -> None:
        self._write("WARN", code, fields)

    def error(self, code: str, /, **fields) -> None:
        self._write("ERROR", code, fields)

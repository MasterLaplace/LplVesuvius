"""A pipeline's report: what each stage did, the equations it applied, and where it stops.

A report is not a journal: it does not say what happened second by second, it says what can be concluded,
stage by stage, and with what. Three rules:

1. **Every equation applied is recorded** with its inputs, its value and the registry fact that carries it:
   read the report and see the formulary at work.
2. **A stage that cannot conclude says so**, with its reason, and never writes zero instead.
3. **Every requirement of the prize has a line**: met, not met, or not measured, and why. What is not produced
   is named, not omitted.
"""
from __future__ import annotations

import json
import platform
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from vesuve import __version__, core
from vesuve.formulary import equation

DONE, STOPPED, SKIPPED, PARTIAL = "done", "stopped", "skipped", "partial"
MET, NOT_MET, NOT_MEASURED, NOT_APPLICABLE = "met", "not met", "not measured", "not applicable"


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, float) and x != x:
        return None
    return x


class Stage:
    def __init__(self, ident: str, name: str, rung: str):
        self.data = {"id": ident, "name": name, "rung": rung, "state": DONE, "equations": [], "outputs": {}}

    def apply(self, ident: str, *args, **shown):
        """Computes an equation of the formulary and records it. `shown`: the inputs to display."""
        e = equation(ident)
        if e.compute is None:
            raise ValueError(f"{ident} is a procedure rule: record it with `record`")
        value = e.compute(*args)
        self.data["equations"].append({"id": e.id, "name": e.name, "latex": e.latex, "fact": e.fact,
                                       "inputs": _jsonable(shown or {"arguments": list(args)}),
                                       "value": _jsonable(value)})
        return value

    def record(self, ident: str, value, **shown) -> None:
        """Records an equation computed elsewhere (the certificate), with what it returned."""
        e = equation(ident)
        self.data["equations"].append({"id": e.id, "name": e.name, "latex": e.latex, "fact": e.fact,
                                       "inputs": _jsonable(shown), "value": _jsonable(value)})

    def note(self, **outputs) -> None:
        self.data["outputs"].update(_jsonable(outputs))

    def stop(self, reason: str) -> None:
        self.data.update({"state": STOPPED, "reason": reason})

    def skip(self, reason: str) -> None:
        self.data.update({"state": SKIPPED, "reason": reason})

    def partial(self, reason: str) -> None:
        self.data.update({"state": PARTIAL, "reason": reason})


class Report:
    def __init__(self, prize: str, inputs: dict, journal=None):
        self.prize, self.journal = prize, journal
        self.start = time.time()
        self.data = {"software": f"vesuve {__version__}", "core": core.version(), "prize": prize,
                     "machine": f"{platform.system()} {platform.machine()} python {platform.python_version()}",
                     "run": getattr(journal, "run", None), "inputs": _jsonable(inputs),
                     "stages": [], "requirements": [], "stop": None}

    @contextmanager
    def stage(self, ident: str, name: str, rung: str = "B1"):
        s = Stage(ident, name, rung)
        t0 = time.monotonic()
        try:
            yield s
        finally:
            s.data["seconds"] = round(time.monotonic() - t0, 3)
            self.data["stages"].append(s.data)
            if self.journal is not None:
                self.journal.info("STAGE", prize=self.prize, stage=ident, state=s.data["state"],
                                  seconds=s.data["seconds"])
            if s.data["state"] == STOPPED and self.data["stop"] is None:
                self.data["stop"] = {"stage": ident, "reason": s.data["reason"]}

    @property
    def stopped(self) -> bool:
        return self.data["stop"] is not None

    def requirement(self, text: str, state: str, measured: str, evidence: str = "") -> None:
        """A requirement of the prize: `met`, `not met`, `not measured` or `not applicable`."""
        self.data["requirements"].append({"requirement": text, "state": state, "what_is_measured": measured,
                                          "evidence": evidence})

    def write(self, folder: Path) -> Path:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.data["seconds"] = round(time.time() - self.start, 2)
        (folder / "report.json").write_text(json.dumps(_jsonable(self.data), ensure_ascii=False, indent=1))
        (folder / "report.md").write_text(as_markdown(self.data))
        return folder / "report.json"


def _value(v) -> str:
    if isinstance(v, float):
        return f"{v:.6g}"
    if isinstance(v, (list, tuple)) and len(v) <= 4:
        return ", ".join(_value(x) for x in v)
    return str(v)


def as_markdown(d: dict) -> str:
    """The readable view of the report, DERIVED from `report.json`: it is not edited."""
    lines = [f"# {d['prize']} — report", "",
             f"`{d['software']}` · core `{d['core']}` · {d['machine']} · {d.get('seconds', '?')} s", ""]
    if d["stop"]:
        lines += [f"> **Stopped at stage {d['stop']['stage']}**: {d['stop']['reason']}", ""]
    lines += ["## The requirements of the prize", "", "| requirement | state | what is measured |", "|---|---|---|"]
    lines += [f"| {x['requirement']} | **{x['state']}** | {x['what_is_measured']} |" for x in d["requirements"]]
    lines += ["", "## The stages", ""]
    for s in d["stages"]:
        lines += [f"### {s['id']} — {s['name']} ({s['rung']}): {s['state']}", ""]
        if s.get("reason"):
            lines += [f"*{s['reason']}*", ""]
        for q in s["equations"]:
            inputs = ", ".join(f"{k} = {_value(v)}" for k, v in q["inputs"].items())
            lines += [f"- **[{q['id']}] {q['name']}** (`{q['fact']}`): $`{q['latex']}`$", "",
                      f"  {inputs} → **{_value(q['value'])}**", ""]
        for k, v in s["outputs"].items():
            text = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            if len(text) > 300:
                text = text[:300] + " …"
            lines.append(f"- `{k}`: {text}")
        lines.append("")
    return "\n".join(lines) + "\n"

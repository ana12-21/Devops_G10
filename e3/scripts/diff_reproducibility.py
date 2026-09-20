#!/usr/bin/env python3
"""Compare two work/<timestamp>/ runs of run_lab.py field by field.

Method:
  - recursively strip the 'ts' fields (they are wall-clock stamps by design)
  - normalise the run-timestamp directory names that appear inside string
    values (they show up in 'cwd' / 'actual_cmd')
  - json.dumps(sort_keys=True, ensure_ascii=False) and byte-compare

Everything compared is already relative to the repository root, so the result
depends only on the toolchain, not on where the repo happens to live.

Usage:
    cd e3
    python scripts/diff_reproducibility.py                 # two newest runs
    python scripts/diff_reproducibility.py <tsA> <tsB>

Output:
    e3/work/reproducibility_diff.log
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent / "work"

FILES = [
    "commit-C0.commands.json",
    "commit-C1.commands.json",
    "commit-C2.commands.json",
    "md-rd.commands.json",
    "commit-C0.observations.json",
    "commit-C1.observations.json",
    "commit-C2.observations.json",
    "md-rd.observations.json",
]

TS_RE = re.compile(r"\d{8}-\d{6}")


def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items() if k != "ts"}
    if isinstance(obj, list):
        return [normalize(x) for x in obj]
    if isinstance(obj, str):
        return TS_RE.sub("<TS>", obj)
    return obj


def pick_dirs(argv: list) -> tuple:
    if len(argv) >= 3:
        return argv[1], argv[2]
    dirs = sorted(d.name for d in WORK.iterdir() if d.is_dir())
    if len(dirs) < 2:
        raise SystemExit(f"need two work/<timestamp>/ directories, found {dirs}")
    return dirs[-2], dirs[-1]


def main(argv: list) -> int:
    name_a, name_b = pick_dirs(argv)
    a = WORK / name_a
    b = WORK / name_b
    if not (a.is_dir() and b.is_dir()):
        raise SystemExit(f"missing dirs: {a.is_dir()=} {b.is_dir()=}")

    lines = []
    lines.append("# reproducibility_diff.log")
    lines.append(f"# generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# method:")
    lines.append("#   1) recursively strip the 'ts' fields")
    lines.append("#   2) replace run-timestamp directory names with <TS> inside")
    lines.append("#      string values ('cwd' / 'actual_cmd')")
    lines.append("#   3) json.dumps(sort_keys=True, ensure_ascii=False) byte-compare")
    lines.append(f"# dirs compared: work/{name_a}  vs  work/{name_b}")
    lines.append("")
    header = f"{'file':42s}  {'left':>6s}  {'right':>6s}  {'status':s}"
    lines.append(header)
    lines.append("-" * len(header))

    all_pass = True
    for fn in FILES:
        fa = a / fn
        fb = b / fn
        if not (fa.exists() and fb.exists()):
            miss = [d for d, f in ((name_a, fa), (name_b, fb)) if not f.exists()]
            lines.append(f"{fn:42s}  MISSING ({','.join(miss)})")
            all_pass = False
            continue
        ja = json.loads(fa.read_text(encoding="utf-8"))
        jb = json.loads(fb.read_text(encoding="utf-8"))
        sa = json.dumps(normalize(ja), sort_keys=True,
                        ensure_ascii=False, separators=(",", ":"))
        sb = json.dumps(normalize(jb), sort_keys=True,
                        ensure_ascii=False, separators=(",", ":"))
        same = sa == sb
        all_pass = all_pass and same
        lines.append(f"{fn:42s}  {len(sa):>6d}  {len(sb):>6d}  "
                     f"{'PASS' if same else 'FAIL'}")

    lines.append("-" * len(header))
    lines.append(f"OVERALL: {'PASS' if all_pass else 'FAIL'}  "
                 f"({len(FILES)} files checked)")
    text = "\n".join(lines) + "\n"
    out = WORK / "reproducibility_diff.log"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"[reproducibility_diff] wrote {out}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

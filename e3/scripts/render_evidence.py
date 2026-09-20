#!/usr/bin/env python3
"""
scripts/render_evidence.py - turn the raw JSON evidence into the plain-text
logs under e3/evidence/.

Why generate instead of hand-write: the JSON files under work/<ts>/ are what
`run_lab.py` actually recorded. Typing the same numbers into narrative files
by hand is how the two drift apart, so the narrative files are derived here
and can be regenerated on demand.

Usage:
    cd e3
    python scripts/render_evidence.py            # newest work/<ts>/ directory
    python scripts/render_evidence.py 20260920-144422

Outputs (overwritten):
    evidence/build_md-rd.txt   md-rd scenario, all steps
    evidence/build_c0.txt      commit-C0, all steps
    evidence/build_c1.txt      commit-C1, all steps
    evidence/build_c2.txt      commit-C2, all steps
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

E3_ROOT = Path(__file__).resolve().parent.parent
WORK = E3_ROOT / "work"
EVIDENCE = E3_ROOT / "evidence"

SCENARIOS = [
    ("md-rd", "build_md-rd.txt", (
        "PPT slide 18-21：MD（改 config.h 后普通 make 不重建）与 "
        "RD（改 unused.h 触发多余编译）两个场景。")),
    ("commit-C0", "build_c0.txt", (
        "PPT slide 24：声明正确的初始提交。clean build 应输出 10"
        "（BASE=10）。")),
    ("commit-C1", "build_c1.txt", (
        "PPT slide 25：main.c 新增 #include \"feature.h\"，Makefile 未同步宣告。"
        "clean build 应输出 12（BASE=10 + FEATURE=2）。"
        "预期发现：main.o 缺 feature.h 依赖。")),
    ("commit-C2", "build_c2.txt", (
        "PPT slide 26-27：只改编译命令（CFLAGS 加 -DMODE=7），源码与 C1 逐字节相同。"
        "普通 make 因时间戳未变而不重编译 → 增量 12；clean build 才拾取新命令 → 19。")),
]


def _fmt(res: dict) -> list:
    out = [f"  $ {res.get('cmd', '')}"]
    if res.get("make_bin"):
        out.append(f"    make_bin : {res['make_bin']}")
    if res.get("actual_cmd"):
        out.append(f"    actual   : {res['actual_cmd']}")
    out.append(f"    cwd      : {res.get('cwd', '')}")
    out.append(f"    exit_code: {res.get('exit_code')}")
    if res.get("note"):
        out.append(f"    note     : {res['note']}")
    stdout = (res.get("stdout") or "").rstrip("\n")
    stderr = (res.get("stderr") or "").rstrip("\n")
    out.append("    stdout   :")
    out.extend(f"      {ln}" for ln in (stdout.splitlines() or ["<empty>"]))
    if stderr:
        out.append("    stderr   :")
        out.extend(f"      {ln}" for ln in stderr.splitlines())
    out.append(f"    ts       : {res.get('ts', '')}")
    return out


def render(ts: str) -> None:
    target = WORK / ts
    if not target.is_dir():
        raise SystemExit(f"no such work directory: {target}")

    for scenario, out_name, blurb in SCENARIOS:
        cmds_path = target / f"{scenario}.commands.json"
        obs_path = target / f"{scenario}.observations.json"
        if not cmds_path.exists():
            raise SystemExit(f"missing {cmds_path}")
        commands = json.loads(cmds_path.read_text(encoding="utf-8"))["commands"]
        observations = json.loads(
            obs_path.read_text(encoding="utf-8"))["observations"]

        lines = [
            f"# {out_name} - {scenario} 场景的完整命令与输出",
            "#",
            f"# 命题：{blurb}",
            "#",
            f"# 数据来源：work/{ts}/{scenario}.commands.json "
            f"+ {scenario}.observations.json",
            "# 本文件由 scripts/render_evidence.py 从上述 JSON 生成，不要手工编辑。",
            "",
            f"## 命令序列（{len(commands)} 条）",
            "",
        ]
        for i, res in enumerate(commands, 1):
            lines.append(f"[step {i}]")
            lines.extend(_fmt(res))
            lines.append("")

        lines.append(f"## 观察结论（{len(observations)} 条）")
        lines.append("")
        lines.append("| # | 步骤 | 实测输出 | 预期 | 说明 |")
        lines.append("|---|------|----------|------|------|")
        for i, ob in enumerate(observations, 1):
            output = ob.get("output", ob.get("stdout", ""))
            lines.append(
                f"| {i} | {ob.get('step', '')} | `{output}` | "
                f"`{ob.get('expected', '')}` | {ob.get('verifies', '')} |")
        lines.append("")

        (EVIDENCE / out_name).write_text("\n".join(lines) + "\n",
                                         encoding="utf-8")
        print(f"[render_evidence] {out_name}  <- work/{ts}/{scenario}.json")


def newest() -> str:
    dirs = sorted(d.name for d in WORK.iterdir() if d.is_dir())
    if not dirs:
        raise SystemExit("no work/<timestamp>/ directory found")
    return dirs[-1]


def main(argv: list) -> int:
    ts = argv[1] if len(argv) > 1 else newest()
    render(ts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

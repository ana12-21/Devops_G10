#!/usr/bin/env python3
"""
scripts/run_lab.py - E3 baseline generator (A10, PPT slide 16-17).

Steps (per slide 16 "A 组步骤 2：运行基线生成器"):
  1.  In fixtures/commits/{C0,C1,C2} run `git init` + commit + tag.
      Backfill the real SHA into each .git_info.txt (slide 5 "保存真实 SHA").
  2.  Create work/<timestamp>/ under E3 root.
  3.  Copy fixtures/md-rd and fixtures/commits/{C0,C1,C2} to work/<timestamp>/.
  4.  Run slide 18-21 (MD/RD) and slide 24-27 (C0/C1/C2) in those copies.
  5.  Write commands.json and observations.json under work/<timestamp>/.
  6.  Print the EVIDENCE_DIR line for the user.

Usage:
    cd e3
    python3 scripts/run_lab.py

Side effects (idempotent for steps 1, 3-5):
    fixtures/commits/{C0,C1,C2}/.git/                  (git init)
    fixtures/commits/{C0,C1,C2}/.git_info.txt          (SHA backfilled)
    work/<timestamp>/                                  (new per run; never overwrites)
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


# ---- paths ---------------------------------------------------------------

E3_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = E3_ROOT / "fixtures"
COMMITS = FIXTURES / "commits"
MD_RD = FIXTURES / "md-rd"
WORK = E3_ROOT / "work"


# ---- small helpers -------------------------------------------------------

def _run(args, cwd=None, check=True, capture=True):
    """Run a command; raise on non-zero exit unless check=False."""
    res = subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    if check and res.returncode != 0:
        sys.stderr.write(f"[run_lab] FAIL: {' '.join(args)} (cwd={cwd})\n")
        if res.stdout:
            sys.stderr.write(res.stdout)
        if res.stderr:
            sys.stderr.write(res.stderr)
        raise SystemExit(res.returncode)
    return res


def _now() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


# ---- step 1: git init + tag in fixtures/commits --------------------------

def init_commit_tag(tag, files, message):
    """git init (idempotent) -> add `files` -> commit -> tag `tag`. Return SHA."""
    cdir = COMMITS / tag
    if not (cdir / ".git").exists():
        _run(["git", "init", "--initial-branch=main"], cwd=cdir)
        _run(["git", "config", "user.email", "e3-a10@devops.local"], cwd=cdir)
        _run(["git", "config", "user.name", "E3 A10"], cwd=cdir)
    _run(["git", "add", "--", *files], cwd=cdir)
    _run(["git", "commit", "-m", message], cwd=cdir, check=False)
    sha = _run(["git", "rev-parse", "HEAD"], cwd=cdir).stdout.strip()
    _run(["git", "tag", "-f", tag], cwd=cdir)
    return sha


def backfill_sha(tag, sha):
    """Replace <TO_BE_FILLED_AFTER_GIT_TAG> in .git_info.txt with `sha`."""
    info = COMMITS / tag / ".git_info.txt"
    if not info.exists():
        return
    text = info.read_text(encoding="utf-8")
    if "<TO_BE_FILLED_AFTER_GIT_TAG>" not in text:
        return
    text = text.replace("<TO_BE_FILLED_AFTER_GIT_TAG>", sha)
    info.write_text(text, encoding="utf-8")


def setup_commits():
    """Create C0/C1/C2 tags and return {tag: sha}."""
    plan = [
        ("C0", ["main.c", "config.h", "Makefile"],
         "C0: declared correctly (PPT slide 24)"),
        ("C1", ["main.c", "config.h", "feature.h", "Makefile"],
         "C1: added #include feature.h, Makefile NOT updated (PPT slide 25)"),
        ("C2", ["main.c", "config.h", "feature.h", "Makefile"],
         "C2: only changed compile command (PPT slide 26)"),
    ]
    shas = {}
    for tag, files, msg in plan:
        sha = init_commit_tag(tag, files, msg)
        shas[tag] = sha
        backfill_sha(tag, sha)
        print(f"[run_lab] tag {tag} -> {sha[:12]}")
    return shas


# ---- step 2-3: copy fixtures to work/<ts> --------------------------------

def stage_workdir(ts):
    """Copy md-rd + C0/C1/C2 into work/<ts>/; return that directory."""
    target = WORK / ts
    if target.exists():
        sys.stderr.write(f"[run_lab] work dir already exists: {target}\n")
        raise SystemExit(2)
    (target / "md-rd").mkdir(parents=True)
    for tag in ("C0", "C1", "C2"):
        (target / tag).mkdir()
    for entry in MD_RD.iterdir():
        if entry.name == ".git_info.txt":
            continue
        shutil.copy2(entry, target / "md-rd" / entry.name)
    for tag in ("C0", "C1", "C2"):
        src = COMMITS / tag
        dst = target / tag
        for entry in src.iterdir():
            if entry.name in (".git", ".git_info.txt"):
                continue
            shutil.copy2(entry, dst / entry.name)
    return target


# ---- step 4: run scenarios ------------------------------------------------

def _record(target, scenario, commands, observations):
    _write_json(target / f"{scenario}.commands.json",
                {"scenario": scenario, "commands": commands})
    _write_json(target / f"{scenario}.observations.json",
                {"scenario": scenario, "observations": observations})


def _find_make():
    """Locate GNU make. Returns path string or None."""
    for name in ("make", "gmake", "mingw32-make"):
        p = shutil.which(name)
        if p:
            return p
    return None


def _find_gcc():
    """Locate gcc. Try PATH first, then common Windows install paths."""
    p = shutil.which("gcc")
    if p:
        return p
    for cand in (
        r"D:\mingw64\bin\gcc.exe",
        r"C:\mingw64\bin\gcc.exe",
        r"C:\Program Files\mingw-w64\mingw64\bin\gcc.exe",
        r"C:\msys64\mingw64\bin\gcc.exe",
        r"C:\MinGW\bin\gcc.exe",
    ):
        if os.path.isfile(cand):
            return cand
    return None


def _parse_cflags(makefile_text):
    """Extract CFLAGS from `CFLAGS ?= ...` line. Default ['-O0','-Wall']."""
    m = re.search(r"^CFLAGS\s*\?=\s*(.+?)\s*$", makefile_text, re.MULTILINE)
    if not m:
        return ["-O0", "-Wall"]
    return m.group(1).strip().split()


def _parse_exe(makefile_text):
    """Find the link target whose only prerequisite is main.o. Default 'app'."""
    m = re.search(r"^([A-Za-z_][\w]*)\s*:\s*main\.o\s*$",
                  makefile_text, re.MULTILINE)
    if m:
        return m.group(1)
    return "app"


def _env_with_toolchain():
    """Return a copy of os.environ with the MinGW toolchain wired in so
    that `mingw32-make` can resolve its default `$(CC)=cc` and `rm`:
      - `CC=gcc` so Makefile's `CC ?= cc` evaluates to gcc (the ?= rule
        only kicks in when CC is not already set, env vars take priority).
      - gcc bin dir prepended to PATH so `gcc`, `rm`, `sh`, etc. resolve.
    """
    env = os.environ.copy()
    gcc = _find_gcc()
    if gcc is None:
        return env
    bin_dir = os.path.dirname(gcc)
    if bin_dir:
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    env["CC"] = "gcc"
    return env


def _run_in(make_args, cwd):
    """Run `make [args]` in cwd. Falls back to gcc + os.remove on Windows
    when GNU make is unavailable. Same return shape either way:
    {cmd, cwd, exit_code, stdout, stderr, ts}.

    On Windows we prefer `mingw32-make` (real dependency tracking — that is
    what makes the MD/RD demo observable). To make it work without polluting
    the user's PATH, we prepend the gcc bin dir to PATH for the subprocess.

    Empty make_args means "build". Several demo Makefiles (e.g. md-rd) have
    `main.o:` as their first target, so `make` alone does NOT link — we
    explicitly invoke the exe target parsed from the Makefile.

    `make clean` is short-circuited to a Python os.remove sweep because
    `rm -f` in Makefile recipes depends on `sh` (CodeBuddy's `safe-bin/rm`
    needs bash) — we keep the demo focused on make's *dependency tracking*
    rather than its recipe shell semantics.
    """
    makefile_text = (cwd / "Makefile").read_text(encoding="utf-8")
    exe_target = _parse_exe(makefile_text)

    # Short-circuit `make clean` to Python (avoid recipe shell dependency).
    if make_args == ["clean"]:
        removed = []
        for f in ("main.o", exe_target):
            p = cwd / f
            if p.exists():
                os.remove(p)
                removed.append(f)
        msg = (f"rm -f main.o {exe_target}  ->  removed: {','.join(removed)}"
               if removed else
               f"rm -f main.o {exe_target}  ->  (nothing to remove)")
        return {
            "cmd": f"rm -f main.o {exe_target}",
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": msg,
            "stderr": "",
            "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        }

    make_bin = _find_make()
    if make_bin is not None:
        # Translate empty build → explicit exe target so linking always happens.
        actual_args = list(make_args)
        if actual_args == []:
            if exe_target and exe_target != "main.o":
                actual_args = [exe_target]

        env = _env_with_toolchain()
        res = subprocess.run(
            [make_bin, *actual_args],
            cwd=str(cwd) if cwd else None,
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            shell=False, env=env)
        if res.returncode != 0:
            sys.stderr.write(f"[run_lab] FAIL: {make_bin} {' '.join(actual_args)} (cwd={cwd})\n")
            if res.stdout:
                sys.stderr.write(res.stdout)
            if res.stderr:
                sys.stderr.write(res.stderr)
        return {
            "cmd": " ".join([make_bin] + (actual_args or make_args)),
            "cwd": str(cwd),
            "exit_code": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        }

    # ---- fallback: drive gcc directly (Windows-friendly) ----------------
    gcc = _find_gcc()
    if gcc is None:
        raise RuntimeError(
            "neither `make` nor `gcc` found on PATH; install MinGW-w64 or "
            "add gcc.exe to PATH, then re-run.")

    makefile_text = (cwd / "Makefile").read_text(encoding="utf-8")
    is_clean = (make_args == ["clean"])
    is_build = (make_args == [] or make_args == ["all"])

    if is_build:
        cflags = _parse_cflags(makefile_text)
        exe = _parse_exe(makefile_text)

        r1 = subprocess.run(
            [gcc, *cflags, "-c", "main.c", "-o", "main.o"],
            cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", shell=False)
        r2 = subprocess.run(
            [gcc, "main.o", "-o", exe],
            cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", shell=False)

        return {
            "cmd": (f"gcc {' '.join(cflags)} -c main.c -o main.o"
                    f"  &&  gcc main.o -o {exe}"),
            "cwd": str(cwd),
            "exit_code": r2.returncode if r2.returncode != 0 else r1.returncode,
            "stdout": (r1.stdout + r2.stdout).strip(),
            "stderr": (r1.stderr + r2.stderr).strip(),
            "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        }

    if is_clean:
        exe = _parse_exe(makefile_text)
        removed = []
        for f in ("main.o", exe):
            p = cwd / f
            if p.exists():
                os.remove(p)
                removed.append(f)
        msg = (f"rm -f main.o {exe}  ->  removed: {','.join(removed)}"
               if removed else
               f"rm -f main.o {exe}  ->  (nothing to remove)")
        return {
            "cmd": f"rm -f main.o {exe}",
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": msg,
            "stderr": "",
            "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        }

    # unknown sub-target — pass-through error so the failure shows up
    return {
        "cmd": f"make {' '.join(make_args)}",
        "cwd": str(cwd),
        "exit_code": -1,
        "stdout": "",
        "stderr": (f"[fallback] unsupported make target: {make_args} "
                   f"(gcc fallback only supports default and `clean`)"),
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
    }


def _run_app(app, cwd):
    """Run the built executable. On Windows, `subprocess.run(['app.exe'],
    cwd=...)` does NOT search the cwd — CreateProcess only consults PATH,
    so a bare name fails with WinError 2 even when `<cwd>/app.exe` exists.
    We always pass the absolute path here.
    """
    name = str(app)                       # e.g. "app" or "main" (Path normalises ./)
    bare = name.replace("./", "").replace(".\\", "")
    candidates = []
    if os.name == "nt":
        # Prefer <bare>.exe (the actual artefact) over <bare>.
        for cand in (bare + ".exe", bare):
            p = Path(cwd) / cand
            if p.is_file():
                candidates.append(str(p))
        if not candidates:
            candidates.append(str(Path(cwd) / (bare + ".exe")))
    else:
        candidates.append(f"./{bare}")

    last_err = None
    res = None
    used = None
    for exe_path in candidates:
        try:
            res = _run([exe_path], cwd=cwd)
            used = exe_path
            break
        except FileNotFoundError as e:
            last_err = e
            continue
    if res is None:
        raise last_err  # type: ignore[misc]

    return {
        "cmd": name,                       # slide-faithful: "app" or "main"
        "actual_cmd": used,                # absolute path we actually ran
        "cwd": str(cwd),
        "exit_code": res.returncode,
        "stdout": res.stdout.strip(),
        "stderr": res.stderr,
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
    }


def _read(path):
    return path.read_text(encoding="utf-8")


def _write(path, text):
    path.write_text(text, encoding="utf-8")


def _touch_after(target, source):
    """Force `source` mtime to be 5s after `target`'s mtime. mingw32-make's
    mtime comparison (and NTFS sub-second resolution quirks) can otherwise
    decide two files written within the same wall-clock second are
    'same age', hiding the intended rebuild. We sidestep that by making
    the gap obvious.
    """
    tgt_mtime = Path(target).stat().st_mtime
    new_mtime = tgt_mtime + 5
    os.utime(Path(source), (new_mtime, new_mtime))


def run_md_rd(target):
    """Slide 18-21: MD/RD demo. Writes md-rd.{commands,observations}.json."""
    cwd = target / "md-rd"
    cmds = []
    obs = []

    # slide 18: make + ./app -> 1
    cmds.append(_run_in([], cwd))
    cmds.append(_run_app(Path("./app"), cwd))
    first = cmds[-1]["stdout"]
    obs.append({"step": "first build", "output": first,
                "expected": "1",
                "verifies": "md-rd demo initial build"})

    # slide 19: edit config.h -> VALUE 2; make; ./app -> still 1 (MD)
    config = _read(cwd / "config.h")
    _write(cwd / "config.h", config.replace("#define VALUE 1", "#define VALUE 2"))
    os.utime(cwd / "config.h", None)
    cmds.append(_run_in([], cwd))
    cmds.append(_run_app(Path("./app"), cwd))
    after_edit = cmds[-1]["stdout"]
    obs.append({
        "step": "edit config.h VALUE=2; make; ./app",
        "output": after_edit,
        "expected": "1 (漏重建 - config.h 未声明为 main.o 的依赖)",
        "verifies": "MISSING config.h (MD)",
    })

    # slide 20: make clean; make; ./app -> 2
    cmds.append(_run_in(["clean"], cwd))
    cmds.append(_run_in([], cwd))
    cmds.append(_run_app(Path("./app"), cwd))
    clean = cmds[-1]["stdout"]
    obs.append({
        "step": "make clean && make && ./app",
        "output": clean,
        "expected": "2 (完整重建拾取新 VALUE)",
        "verifies": "完整重建可观察到新值, 与漏重建对比",
    })

    # slide 21: edit unused.h comment only; make -> re-runs cc -c main.c (RD)
    unused = _read(cwd / "unused.h")
    _write(cwd / "unused.h", unused.replace("still unused", "still unused (edited)"))
    _touch_after(cwd / "main.o", cwd / "unused.h")
    cmds.append(_run_in([], cwd))
    rd_stdout = cmds[-1]["stdout"]
    obs.append({
        "step": "edit unused.h comment; make",
        "stdout": rd_stdout,
        "expected": "cc -c main.c -o main.o 重新执行 (多余编译)",
        "verifies": "REDUNDANT unused.h (RD)",
    })

    # restore config.h to VALUE 1 + clean for next runs
    _write(cwd / "config.h", config)
    _write(cwd / "unused.h", unused)
    cmds.append(_run_in(["clean"], cwd))

    _record(target, "md-rd", cmds, obs)


def run_commit(target, tag, expected_clean, expected_incremental=None, note=None):
    """Slide 24-27: C0/C1/C2 demo."""
    cwd = target / tag
    scenario = f"commit-{tag}"
    cmds = []
    obs = []

    cmds.append(_run_in(["clean"], cwd))
    cmds.append(_run_in([], cwd))
    cmds.append(_run_app(Path("./main"), cwd))
    clean_out = cmds[-1]["stdout"]
    verifies_clean = f"{tag} clean baseline"
    if note:
        verifies_clean += " | NOTE: " + note
    obs.append({
        "step": "clean build + run",
        "output": clean_out,
        "expected": str(expected_clean),
        "verifies": verifies_clean,
    })

    if expected_incremental is not None:
        cmds.append(_run_in([], cwd))
        cmds.append(_run_app(Path("./main"), cwd))
        incr_out = cmds[-1]["stdout"]
        obs.append({
            "step": "second make without clean (incremental)",
            "output": incr_out,
            "expected": str(expected_incremental),
            "verifies": f"{tag} 命令变化未触发普通重建",
        })

    cmds.append(_run_in(["clean"], cwd))
    _record(target, scenario, cmds, obs)


def run_scenarios(target):
    run_md_rd(target)
    # Slide 27 expected table.
    # NOTE on C2: PPT slide 26 says clean=19 (MODE=7), but the fixture's
    # config.h contains `#define MODE 0` which overrides the -DMODE=7 from
    # CFLAGS — the source-level redefinition wins. Record the *real* output
    # and flag the conflict in the verifies field so the discrepancy is
    # visible instead of silently matching the PPT claim.
    run_commit(target, "C0", expected_clean="BASE=10 MODE=0")
    run_commit(target, "C1", expected_clean="BASE=10 FEATURE=2 MODE=0")
    run_commit(target, "C2",
               expected_clean="BASE=10 FEATURE=2 MODE=0",
               expected_incremental="BASE=10 FEATURE=2 MODE=0",
               note=("PPT slide 26 says clean=19 (MODE=7) but config.h's "
                     "#define MODE 0 overrides -DMODE=7; clean build yields "
                     "the same MODE=0 as the incremental build."))


# ---- entry ---------------------------------------------------------------

def main():
    if not (FIXTURES / "md-rd" / "oracle.json").exists():
        sys.stderr.write("[run_lab] missing fixtures/md-rd/oracle.json\n")
        return 1
    print("[run_lab] step 1/3: git init + tag C0/C1/C2 ...")
    setup_commits()
    ts = _now()
    print(f"[run_lab] step 2/3: staging work/{ts} ...")
    target = stage_workdir(ts)
    print("[run_lab] step 3/3: running md-rd + C0/C1/C2 scenarios ...")
    run_scenarios(target)
    # Final summary line - slide 16 expects EVIDENCE_DIR on the last line.
    print(f"EVIDENCE_DIR={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
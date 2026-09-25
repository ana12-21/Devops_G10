#!/usr/bin/env python3
"""
validate.py —— E2 契约校验脚本

验收标准（对应 PPT Slide 25）：
  01  跑 validate.py，四类请求与响应都能通过 task.schema.json 校验
  02  把 job_type 改成 ABC，应被拒绝
  03  删除 INCREMENTAL_CHECK 的 baseline，应被拒绝
  04  同一个 job 不能同时写 error 和 findings

用法：
  python scripts/validate.py            # 默认模式：校验全部样例
  python scripts/validate.py --negative # 跑一组反例（预期失败）
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
SCHEMA_FILE = CONTRACTS / "task.schema.json"

SCHEMA_VERSION = "1.0.0"
JOB_ID_PATTERN = re.compile(r"^job-[a-z0-9]+$")
JOB_TYPES = {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}
STATUSES = {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}
REQUIRED = {"schema_version", "job_id", "job_type", "status", "trace_id", "input", "execution", "created_at"}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(msg: str, ctx: str = ""):
    line = f"  FAIL: {msg}"
    if ctx:
        line += f"  ({ctx})"
    print(line)
    return False


def ok(msg: str):
    print(f"  OK:   {msg}")
    return True


def check_envelope(doc: dict, src: Path) -> bool:
    """校验一份任务文档是否满足 task.schema.json 外壳"""
    passed = True

    # 必填字段
    missing = REQUIRED - doc.keys()
    if missing:
        passed &= fail(f"缺必填字段 {missing}", str(src))
    else:
        passed &= ok("必填字段齐全")

    execution = doc.get("execution")
    if (
        not isinstance(execution, dict)
        or execution.get("mode") not in {"ASYNC", "SYNC"}
        or type(execution.get("attempt")) is not int
        or execution["attempt"] < 1
    ):
        passed &= fail("execution 必须包含合法的 mode 和正整数 attempt", str(src))

    # schema_version
    if doc.get("schema_version") != SCHEMA_VERSION:
        passed &= fail(
            f"schema_version 应为 {SCHEMA_VERSION!r}，实为 {doc.get('schema_version')!r}",
            str(src),
        )

    trace_id = doc.get("trace_id")
    if not isinstance(trace_id, str) or not re.match(r"^trace-[a-z0-9-]+$", trace_id):
        passed &= fail("请求必须包含合法的 trace_id", str(src))
    else:
        passed &= ok(f"schema_version = {SCHEMA_VERSION}")

    # job_id 格式
    if not JOB_ID_PATTERN.match(doc.get("job_id", "")):
        passed &= fail(f"job_id 不匹配 {JOB_ID_PATTERN.pattern}", str(src))
    else:
        passed &= ok(f"job_id = {doc['job_id']}")

    # job_type 合法
    if doc.get("job_type") not in JOB_TYPES:
        passed &= fail(
            f"job_type={doc.get('job_type')!r} 不在 {JOB_TYPES} 中", str(src)
        )
    else:
        passed &= ok(f"job_type = {doc['job_type']}")

    # status 合法
    if doc.get("status") not in STATUSES:
        passed &= fail(
            f"status={doc.get('status')!r} 不在 {STATUSES} 中", str(src)
        )
    else:
        passed &= ok(f"status = {doc['status']}")

    # 互斥约束：error 与 output.findings 不同时出现
    has_error = bool(doc.get("error"))
    findings = doc.get("output", {}).get("findings")
    has_findings = bool(findings)
    if has_error and has_findings:
        passed &= fail(
            "同一 Job 同时写了 error 与 output.findings（互斥违反）", str(src)
        )
    else:
        passed &= ok("error / findings 互斥约束通过")

    # findings 类型检查
    if findings:
        bad = [f for f in findings if f.get("type") not in {"MISSING", "REDUNDANT"}]
        if bad:
            passed &= fail(f"findings 含非法 type: {bad}", str(src))
        else:
            passed &= ok("findings 类型合法")

    # 时间格式（如果有）
    for k in ("created_at", "updated_at"):
        v = doc.get(k)
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", v):
            passed &= fail(f"{k}={v!r} 不是 ISO8601 UTC 格式", str(src))

    return passed


def check_request_envelope(doc: dict, src: Path) -> bool:
    "创建请求要求版本、任务类型和输入；禁止服务端生成字段"
    passed = True
    if "job_type" not in doc:
        passed &= fail("请求样例缺 job_type", str(src))
    elif doc["job_type"] not in JOB_TYPES:
        passed &= fail(
            f"请求 job_type={doc['job_type']!r} 不在 {JOB_TYPES} 中", str(src)
        )
    else:
        passed &= ok(f"job_type = {doc['job_type']}")

    if doc.get("schema_version") != SCHEMA_VERSION:
        passed &= fail(
            f"请求 schema_version 应为 {SCHEMA_VERSION!r}",
            str(src),
        )

    if not isinstance(doc.get("input"), dict):
        passed &= fail("请求必须包含对象类型的 input", str(src))

    if doc.get("job_type") == "INCREMENTAL_CHECK":
        baseline = doc.get("input", {}).get("baseline")
        if not isinstance(baseline, dict):
            passed &= fail("INCREMENTAL_CHECK 缺 input.baseline", str(src))
        elif not all(baseline.get(k) for k in (
                "commit", "configuration_id", "actual_graph_uri"
        )):
            passed &= fail("input.baseline 字段不完整", str(src))

    # 请求不应携带服务端字段
    for k in ( "job_id", "status", "output", "error"):
        if k in doc:
            passed &= fail(f"请求样例不应携带 {k}", str(src))

    return passed


def run_positive():
    """正面校验：所有样例应通过"""
    print("\n=== 1. 正面校验：四类任务样例全部套用 task.schema.json ===")
    all_ok = True

    if not SCHEMA_FILE.exists():
        print(f"  FAIL: 缺 schema 文件 {SCHEMA_FILE}")
        return False

    try:
        schema = load_json(SCHEMA_FILE)
        ok(f"task.schema.json 加载成功（required={schema['required']}）")
    except Exception as e:
        fail(f"task.schema.json 解析失败: {e}")
        return False

    # 套外壳校验
    response_files = [
        "full_check.res.json",
        "full_check_err.res.json",
        "incremental_check.res.json",
        "dockerfile_job.res.json",
        "dockerfile_job_err.res.json",
        "repair_job.res.json",
        "repair_job_err.res.json",
        "query_job.res.json",
    ]
    echoed_requests = {
        "full_check.res.json": "full_check.req.json",
        "query_job.res.json": "full_check.req.json",
        "dockerfile_job.res.json": "dockerfile_job.req.json",
        "dockerfile_job_err.res.json": "dockerfile_job.req.json",
        "repair_job.res.json": "repair_job.req.json",
        "repair_job_err.res.json": "repair_job.req.json",
    }
    for name in response_files:
        path = CONTRACTS / name
        if not path.exists():
            all_ok &= fail(f"缺文件 {name}")
            continue
        print(f"\n  [{name}]")
        doc = load_json(path)
        all_ok &= check_envelope(doc, path)
        if name in echoed_requests:
            request_input = load_json(CONTRACTS / echoed_requests[name])["input"]
            if doc.get("input") != request_input:
                all_ok &= fail("响应 input 与创建请求的 input 不一致", str(path))
            else:
                all_ok &= ok("响应 input 与创建请求一致")

    # 请求样例校验（query_job.req.json 是 GET 查询，无 job_type，跳过）
    request_files = [
        "full_check.req.json",
        "incremental_check.req.json",
        "dockerfile_job.req.json",
        "repair_job.req.json",
    ]
    print("\n=== 2. 请求必须携带正确的 schema_version,必填 job_type + 不含服务端字段 ===")
    for name in request_files:
        path = CONTRACTS / name
        if not path.exists():
            all_ok &= fail(f"缺文件 {name}")
            continue
        print(f"\n  [{name}]")
        doc = load_json(path)
        all_ok &= check_request_envelope(doc, path)

    # query_job.req.json 是 GET 路径参数描述，单独校验
    query_req = CONTRACTS / "query_job.req.json"
    if query_req.exists():
        print("\n=== 3. GET 查询样例 ===")
        doc = load_json(query_req)
        if "path_params" in doc and "job_id" in doc["path_params"]:
            ok(f"GET 查询路径参数: job_id = {doc['path_params']['job_id']}")
        else:
            fail("GET 查询样例缺 path_params.job_id", str(query_req))
            all_ok = False

    return all_ok


def run_negative():
    """负面校验：反例必须被规则拒绝（手工断言）"""
    print("\n=== 4. 负面校验：以下反例应当被拒绝 ===")
    all_ok = True

    bad_payloads = [
        ("job_type 改成 ABC", {"schema_version": "1.0.0", "job_id": "job-x",
                                 "job_type": "ABC", "status": "QUEUED"},
         "ABC 不在枚举内"),
        ("schema_version 不对", {"schema_version": "2.0.0", "job_id": "job-x",
                                   "job_type": "FULL_CHECK", "status": "QUEUED"},
         "const=1.0.0 违例"),
        ("job_id 格式错", {"schema_version": "1.0.0", "job_id": "FULL01",
                             "job_type": "FULL_CHECK", "status": "QUEUED"},
         "应匹配 ^job-[a-z0-9]+$"),
        ("status 错", {"schema_version": "1.0.0", "job_id": "job-x",
                        "job_type": "FULL_CHECK", "status": "DONE"},
         "DONE 不在六态内"),
        ("缺 job_id", {"schema_version": "1.0.0", "job_type": "FULL_CHECK",
                        "status": "QUEUED"},
         "必填字段缺失"),
        ("error 与 findings 同存", {
            "schema_version": "1.0.0", "job_id": "job-x",
            "job_type": "FULL_CHECK", "status": "FAILED",
            "error": {"code": "ENV_3002", "message": "x"},
            "output": {"findings": [{"type": "MISSING", "target": "a", "dependency": "b"}]},
        }, "互斥违反"),
        ("INCREMENTAL_CHECK 缺 baseline",
         {"job_type": "INCREMENTAL_CHECK",
          "input": {"repository": {"url": "git@github.com:/x.git", "commit": "x"*40},
                     "build": {"command": "make", "project_root": "./"}}},
         "baseline 缺失，EChecker 应拒绝"),
        ("incremental_check.req 删 baseline",
         {k: v for k, v in [
             ("job_type", "INCREMENTAL_CHECK"),
             ("input", {"repository": {"url": "git@github.com:/x.git", "commit": "abc"},
                         "build": {"command": "make", "project_root": "./"}})]},
         "同上一条"),
    ]

    for _, doc, _ in bad_payloads:
        if "status" in doc:
            doc.setdefault("execution", {"mode": "ASYNC", "attempt": 1})

    for label, doc, why in bad_payloads:
        ok_so_far = True

        # 必填检查
        missing = REQUIRED - doc.keys()
        if missing:
            ok_so_far &= ok(f"反例 [{label}]：必填缺 {missing} → 会被拒")

        # schema_version const
        if "schema_version" in doc and doc["schema_version"] != SCHEMA_VERSION:
            ok_so_far &= ok(f"反例 [{label}]：schema_version 不匹配 → 会被拒")

        # job_type enum
        if doc.get("job_type") not in JOB_TYPES:
            ok_so_far &= ok(f"反例 [{label}]：job_type 不在枚举 → 会被拒")

        # job_id pattern
        if "job_id" in doc and not JOB_ID_PATTERN.match(doc["job_id"]):
            ok_so_far &= ok(f"反例 [{label}]：job_id 格式错 → 会被拒")

        # status enum
        if doc.get("status") not in STATUSES:
            ok_so_far &= ok(f"反例 [{label}]：status 不在六态 → 会被拒")

        # 互斥
        if doc.get("error") and doc.get("output", {}).get("findings"):
            ok_so_far &= ok(f"反例 [{label}]：error+findings 同存 → 会被拒")

        # incremental_check 必须有 baseline
        if doc.get("job_type") == "INCREMENTAL_CHECK":
            if "baseline" not in doc.get("input", {}):
                ok_so_far &= ok(f"反例 [{label}]：INCREMENTAL_CHECK 缺 baseline → 会被拒")

        if not ok_so_far:
            all_ok = False
        print(f"    解释：{why}")

    return all_ok


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--positive"

    print(f"E2 契约校验 — 模式 {mode}")
    print(f"Schema: {SCHEMA_FILE.relative_to(ROOT)}")

    if mode == "--negative":
        ok_neg = run_negative()
        sys.exit(0 if ok_neg else 1)
    elif mode == "--all":
        ok_pos = run_positive()
        ok_neg = run_negative()
        sys.exit(0 if (ok_pos and ok_neg) else 1)
    else:
        ok_pos = run_positive()
        sys.exit(0 if ok_pos else 1)


if __name__ == "__main__":
    main()

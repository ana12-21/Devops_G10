# 最小检查说明

> E2 交付项：说明 `scripts/validate.py` 应当检查什么、如何判定通过，
> 以及如何用一句话解释"**MD 不等于工具执行失败**"。
> 责任方：A 组。**需与 B10 确认**（B 组需提供对应的 DRAFT / REPAIR 反例）。

## 1. 检查目标

E2 规定的最小检查共 5 组，**缺一不可**：

| 编号 | 检查项 | 对应 E2 规范点 |
|------|--------|----------------|
| G1 | 四类任务的**有效样例**必须通过 | 有效样例通过 |
| G2 | **无效输入**必须被拒绝 | 无效输入被拒绝 |
| G3 | `job_type` 改成 `ABC` 必须被拒绝 | 枚举校验 |
| G4 | 增量任务**删除 `baseline`** 必须被拒绝 | 必填校验 |
| G5 | 能解释"**MD ≠ 执行失败**" | 错误/发现分离 |

其中 G1 是**正面**检查（期望通过），G2–G4 是**负面**检查（期望失败），
G5 是**语义**检查（用样例对证，不是断言）。

## 2. 检查清单

### G1 — 有效样例必须通过

对每个样例断言以下 7 条：

| # | 断言 | 期望 |
|---|------|------|
| 1 | 必填字段齐全 | `schema_version` / `job_id` / `job_type` / `status` 全部存在 |
| 2 | `schema_version` 合法 | 等于当前契约版本（`1.0.0`） |
| 3 | `job_id` 格式合法 | 匹配 `^job-[a-z0-9]+$` |
| 4 | `job_type` 在枚举内 | `DRAFT` / `FULL_CHECK` / `INCREMENTAL_CHECK` / `REPAIR` |
| 5 | `status` 在六态内 | `QUEUED` / `RUNNING` / `SUCCEEDED` / `FAILED` / `TIMED_OUT` / `CANCELLED` |
| 6 | `error` 与 `output.findings` 互斥 | 不同时出现 |
| 7 | `findings[].type` 合法 | 仅 `MISSING` / `REDUNDANT` |

额外规则（当前脚本未覆盖，见第 5 节）：

| # | 断言 | 期望 |
|---|------|------|
| 8 | `SUCCEEDED` 必须带 `output` | 成功必有产出 |
| 9 | `FAILED` / `TIMED_OUT` 必须带 `error` | 失败必有原因 |
| 10 | `QUEUED` 不得带 `output` | 创建即返回，尚未执行 |
| 11 | 请求样例不得携带服务端字段 | 无 `job_id` / `status` / `schema_version` / `output` / `error` |

### G2 — 无效输入必须被拒绝

| 反例 | 违反点 | 期望错误码 |
|------|--------|------------|
| `negative/invalid_job_type.req.json` | `job_type = "ABC"` | `SCHEMA_1001` |
| `negative/missing_baseline.req.json` | 增量缺 `input.baseline` | `BASELINE_2001` |
| `negative/error_and_findings.res.json` | `error` 与 `findings` 同存 | `SCHEMA_1001` |

另需覆盖（脚本内已有断言）：

| 反例 | 违反点 |
|------|--------|
| `schema_version = "2.0.0"` | 版本不符 |
| `job_id = "FULL01"` | 不匹配 `^job-[a-z0-9]+$` |
| `status = "DONE"` | 不在六态内 |
| 缺 `job_id` | 必填字段缺失 |

### G3 — `job_type` 非法必须被拒绝

```
输入：{ "job_type": "ABC", ... }
期望：拒绝，返回 SCHEMA_1001，status = FAILED，不进入 RUNNING
理由：task.schema.json 中 job_type 为 enum；服务端不得猜测意图、不得降级为全量检测
```

### G4 — 增量任务缺 `baseline` 必须被拒绝

```
输入：{ "job_type": "INCREMENTAL_CHECK", "input": { "repository": {...}, "build": {...} } }
期望：拒绝，返回 BASELINE_2001，status = FAILED，不进入 RUNNING
理由：增量检测的语义是"相对某历史基线求差"；缺 baseline 则
      new_findings / eliminated_findings 无法定义，结果不可解释。
      EChecker 不得退化为全量检测。
```

### G5 — 语义检查：MD ≠ 执行失败

这是**唯一不能用断言表达的检查**，需用样例对证：

| 情形 | 样例文件 | `status` | `error` | `findings` |
|------|----------|----------|---------|------------|
| 检测到缺失依赖 | `md_report.sample.json` | `SUCCEEDED` | **无** | 有（MISSING） |
| 分析器崩溃 | `analysis_err.res.json` | `FAILED` | `ANALYSIS_5001` | **无** |
| 两者同存（非法） | `negative/error_and_findings.res.json` | — | 有 | 有 |

**标准表述**（可直接写进汇报）：

> 检测出 `MISSING` / `REDUNDANT` 是工具**正常跑完**后发现的业务问题，属于 `SUCCEEDED` 的合法产出；
> 只有平台或工具**自身故障**（`ENV_3002` / `EXEC_4002` / `ANALYSIS_5001`）才写 `job.error`。
> 因此"发现数 > 0"**绝不能**作为判断任务失败的依据。

## 3. 伪代码

```python
# ========== 常量 ==========
REQUIRED_SERVER_FIELDS = {"schema_version", "job_id", "job_type", "status"}
SERVER_ONLY_FIELDS = {"schema_version", "job_id", "status", "output", "error"}
JOB_TYPES = {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}
STATUSES = {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}
FINDING_TYPES = {"MISSING", "REDUNDANT"}
TERMINAL_FAIL = {"FAILED", "TIMED_OUT"}

def check_response(doc) -> bool:
    ok = True
    ok &= REQUIRED_SERVER_FIELDS <= doc.keys()
    ok &= doc["schema_version"] == SCHEMA_VERSION
    ok &= matches(doc["job_id"], r"^job-[a-z0-9]+$")
    ok &= doc["job_type"] in JOB_TYPES
    ok &= doc["status"] in STATUSES

    has_error    = bool(doc.get("error"))
    findings     = doc.get("output", {}).get("findings", [])
    delta_new    = doc.get("output", {}).get("delta", {}).get("new_findings", [])

    # 规则 R1：成功必须有产出
    if doc["status"] == "SUCCEEDED":
        ok &= "output" in doc
    # 规则 R2：失败必须有原因
    if doc["status"] in TERMINAL_FAIL:
        ok &= has_error
    # 规则 R3：成功不得带 error
    if doc["status"] == "SUCCEEDED":
        ok &= not has_error
    # 规则 R4：创建即返回，不得带产出
    if doc["status"] == "QUEUED":
        ok &= "output" not in doc
    # 规则 R5：error 与 findings 互斥
    if has_error:
        ok &= not findings and not delta_new
    # 规则 R6：发现类型合法
    ok &= all(f["type"] in FINDING_TYPES for f in findings + delta_new)
    return ok


def check_request(doc) -> bool:
    ok = True
    ok &= doc.get("job_type") in JOB_TYPES
    ok &= not (SERVER_ONLY_FIELDS & doc.keys())      # 请求不得带服务端字段
    return ok


def check_incremental_baseline(doc) -> bool:
    """G4：增量任务必须带 baseline，且 baseline 内字段齐全"""
    if doc.get("job_type") != "INCREMENTAL_CHECK":
        return True
    baseline = doc.get("input", {}).get("baseline")
    if baseline is None:
        reject("BASELINE_2001", "input.baseline 缺失")
        return False
    required = {"commit", "configuration_id", "actual_graph_uri"}
    if not required <= baseline.keys():
        reject("BASELINE_2001", f"baseline 缺 {required - baseline.keys()}")
        return False
    return True


# ========== 主流程 ==========
def run_positive():
    """G1：所有有效样例必须通过"""
    for f in RESPONSE_SAMPLES:        # 见第 4 节文件清单
        assert check_response(load(f)), f"{f} 应通过"
    for f in REQUEST_SAMPLES:
        assert check_request(load(f)), f"{f} 应通过"
    return True


def run_negative():
    """G2 + G3 + G4：所有反例必须被拒绝"""
    for f in NEGATIVE_SAMPLES:
        doc = load(f)
        assert not (check_response(doc) and check_request(doc)), f"{f} 应被拒绝"
        assert not check_incremental_baseline(doc), f"{f} 应被拒绝"
    return True


def run_semantic():
    """G5：MD ≠ 执行失败，用样例对证"""
    md = load("contracts/md_report.sample.json")
    assert md["summary"]["missing_count"] > 0        # 确实发现了问题
    assert TERMINAL_FAIL & {md["status"]} == set()   # 但状态不是失败
    assert "error" not in md                          # 也没有系统错误

    err = load("contracts/analysis_err.res.json")
    assert err["status"] == "FAILED"
    assert err["error"]["code"] == "ANALYSIS_5001"
    assert not err.get("output", {}).get("findings")  # 崩溃时无发现
    return True


def main():
    return run_positive() and run_negative() and run_semantic()
```

## 4. 文件清单（检查对象）

### 正面样例（G1，期望通过）

| 类别 | 文件 |
|------|------|
| 请求 | `full_check.req.json`、`incremental_check.req.json`、`dockerfile_job.req.json`、`repair_job.req.json` |
| 创建响应 | `full_check.created.res.json`、`incremental_check.created.res.json` |
| 查询响应 | `query_job.res.json` |
| 成功响应 | `full_check.res.json`、`incremental_check.res.json`、`dockerfile_job.res.json`、`repair_job.res.json` |
| 失败响应 | `full_check_err.res.json`、`analysis_err.res.json`、`incremental_check_err.res.json`、`repair_job_err.res.json` |
| 产物样例 | `md_report.sample.json`、`incremental_report.sample.json` |
| 错误对象 | `errors/ENV_3002.error.json`、`errors/EXEC_4002.error.json`、`errors/ANALYSIS_5001.error.json` |

### 负面样例（G2–G4，期望被拒绝）

| 文件 | 违反点 |
|------|--------|
| `negative/invalid_job_type.req.json` | `job_type = "ABC"` |
| `negative/missing_baseline.req.json` | 增量缺 `baseline` |
| `negative/error_and_findings.res.json` | `error` 与 `findings` 同存 |

## 5. 当前脚本的覆盖差距（待补）

`scripts/validate.py` 现状：**正面 8 响应 + 4 请求 + 1 查询，负面 8 条硬编码反例，退出码 0**。
以下尚未覆盖，列为待办：

| # | 差距 | 影响 |
|---|------|------|
| S-01 | 反例**硬编码在 Python 里**，未读取 `negative/*.json` | 落盘反例与脚本可能脱节 |
| S-02 | 未校验 `*.created.res.json`（202 响应） | 新增样例无覆盖 |
| S-03 | 未校验 `analysis_err.res.json`、`incremental_check_err.res.json` | 失败样例无覆盖 |
| S-04 | 未校验 `*.sample.json`（ERROR_REPORT） | 关键产物无覆盖 |
| S-05 | 未校验 `errors/*.error.json` | 错误对象无覆盖 |
| S-06 | 未实现规则 R1 / R2 / R3 / R6（`SUCCEEDED` 带 output 等） | 状态机不变量未强制 |
| S-07 | 互斥检查只读 `output.findings`，**漏掉 `output.delta.new_findings`** | 增量任务可绕过互斥 |
| S-08 | 未用 `jsonschema` 库真正消费 `task.schema.json`，规则靠 Python 复刻 | Schema 与脚本可能不一致 |

> ⚠️ S-07 是**实际漏洞**：一份同时含 `job.error` 与 `output.delta.new_findings`
> 的增量响应，当前脚本会判为"通过"。修复方式是把互斥断言扩展到 `delta`。

## 6. 手工复核步骤

```bash
# 1. 全量检查（正面 + 负面）
python e2/scripts/validate.py --all
# 期望：退出码 0

# 2. 只跑正面
python e2/scripts/validate.py
# 期望：退出码 0

# 3. 只跑负面
python e2/scripts/validate.py --negative
# 期望：退出码 0，且每条反例都打印"会被拒"

# 4. 独立确认所有 JSON 语法
python -c "import json,pathlib;[json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('e2/contracts').rglob('*.json')];print('all valid')"
```

## 7. 与 B10 确认事项

| 编号 | 待确认 | 状态 |
|------|--------|------|
| M-01 | DRAFT / REPAIR 的反例样例（B 组提供） | ⏳ 待 B 组提供 |
| M-02 | 是否统一由本项目提供 `validate.py`，还是各自维护 | ⏳ 待 B 组确认 |
| M-03 | 第 5 节 S-01 ~ S-08 的修复排期 | ⏳ 待定 |

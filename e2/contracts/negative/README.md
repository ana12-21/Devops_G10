# 反例集合（A 组）

> 本目录存放**故意违规**的请求/响应样例，用于证明契约的拒绝行为可复现。
> 每个文件都是语法正确的 JSON，但违反了 `contracts/task.schema.json` 或契约约定，**必须被服务端拒绝**。

## 反例清单

| 文件 | 违反点 | 期望错误码 | 期望行为 |
|------|--------|-----------|----------|
| `invalid_job_type.req.json` | `job_type = "ABC"` 不在枚举内 | `SCHEMA_1001` | 校验阶段拒绝，不进入 RUNNING |
| `missing_baseline.req.json` | `INCREMENTAL_CHECK` 缺 `input.baseline` | `BASELINE_2001` | EChecker 拒绝，不得退化为全量检测 |
| `error_and_findings.res.json` | `job.error` 与 `output.findings` 同存 | `SCHEMA_1001` | 互斥违反，不得作为合法响应 |

## 关键解释：MD ≠ 工具执行失败

反例 `error_and_findings.res.json` 是最容易被误解的一条，因此单独说明：

| 情形 | `status` | `job.error` | `output.findings` | 含义 |
|------|----------|-------------|-------------------|------|
| 检测到缺失依赖 | `SUCCEEDED` | 空 | 有（MISSING） | **工具正常完成**，发现了问题 |
| 分析器崩溃 | `FAILED` | `ANALYSIS_5001` | 空 | **工具失败了**，没有产出可信结论 |
| 两者同存 | — | 有 | 有 | **非法**：无法判断任务成功还是失败 |

结论：
- 检测出 `MISSING` / `REDUNDANT` 是**正常业务产出**，任务状态仍为 `SUCCEEDED`。
- 只有平台/工具自身故障（`ENV_3002` / `EXEC_4002` / `ANALYSIS_5001`）才写 `job.error`。
- 因此"发现数 > 0"绝不能作为判断任务失败的依据。

## 使用方式

```bash
# 逐个喂给服务端，或喂给 scripts/validate.py 的负面校验逻辑
python e2/scripts/validate.py --negative
```

> `validate.py` 目前以内置断言方式表达反例；本目录提供的是**落盘可复现**版本，两者结论应一致。

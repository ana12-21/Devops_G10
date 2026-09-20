# E2 A-group completion pack

本目录只补充 A 组负责的 E2 内容：BuildChecker 全量依赖检测和 EChecker 跨提交增量检测。

## 文件说明

| 文件 | 作用 |
|------|------|
| `a_group_contracts.md` | 说明 A 组负责的两个服务、输入输出、产物和验收条件。 |
| `paper_to_a_contract_mapping.md` | 将 BuildChecker 和 EChecker 两篇论文中的关键概念映射到 A 组契约字段。 |
| `strict_a_group.schema.json` | A 组补充版严格契约，只覆盖 `FULL_CHECK` 和 `INCREMENTAL_CHECK`。 |
| `openapi_a_group.yaml` | A 组两个创建接口和查询接口的 OpenAPI 片段。 |
| `samples/a_group_trace.sample.json` | 从 C0 全量检测到 C1 增量检测的 A 组端到端样例。 |
| `samples/baseline_mismatch.err.res.json` | 增量检测 baseline commit 与实际图元数据不匹配时的失败响应。 |
| `scripts/validate_a_group_completion.py` | 只校验本目录新增 A 组样例的脚本。 |

## 设计边界

- 不替换原有 `../task.schema.json`，只提供 A 组更严格的补充约束。
- 不修改原有请求、响应、错误码和验证脚本。
- 只覆盖 A 组检测契约和 A 组产出。
- `MISSING` / `REDUNDANT` 是分析发现，不写入 `job.error`。系统执行失败才写 `job.error`。

## 验证方式

在仓库根目录运行：

```powershell
python e2\contracts\e2_completion_pack\scripts\validate_a_group_completion.py
```

期望输出：

```text
OK A-group trace
OK baseline mismatch error
OK A-group strict contract pack
```

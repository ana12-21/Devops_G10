# A 组契约补充

本文件只描述 A 组负责的 BuildChecker 和 EChecker 两项检测服务。

## A 组服务

| 服务 | job_type | 论文基础 | A 组职责 |
|------|----------|----------|----------|
| BuildChecker | `FULL_CHECK` | TSE BuildChecker | 对固定仓库提交和固定构建配置执行全量依赖检测，产出实际依赖图、声明依赖图和 MD/RD 报告。 |
| EChecker | `INCREMENTAL_CHECK` | ISSTA 2024 incremental detection | 基于历史实际依赖图和新提交执行增量检测，产出新增、消除和未变的依赖发现，并更新实际依赖图。 |

## FULL_CHECK 输入

| 字段 | 必填 | 说明 |
|------|------|------|
| `job_type` | 是 | 固定为 `FULL_CHECK`。 |
| `input.repository.url` | 是 | 被检测仓库地址。 |
| `input.repository.commit` | 是 | 完整 40 位 commit。 |
| `input.build.command` | 是 | clean build 命令。 |
| `input.build.project_root` | 是 | 项目根目录。 |
| `input.configuration_id` | 是 | 构建配置 ID，例如 `cc-MODE0`。 |

## FULL_CHECK 输出

| 产物 | 类型 | 说明 |
|------|------|------|
| 实际依赖图 | `ACTUAL_GRAPH` | 从构建执行中得到的实际依赖。 |
| 声明依赖图 | `DECLARED_GRAPH` | 从 Makefile 等构建脚本中得到的声明依赖。 |
| 错误报告 | `ERROR_REPORT` | 包含 `MISSING` 和 `REDUNDANT` findings。 |
| 构建日志 | `BUILD_LOG` | 用于复核分析过程。 |

## INCREMENTAL_CHECK 输入

| 字段 | 必填 | 说明 |
|------|------|------|
| `job_type` | 是 | 固定为 `INCREMENTAL_CHECK`。 |
| `input.repository.commit` | 是 | 当前提交，例如 C1 或 C2。 |
| `input.baseline.commit` | 是 | 历史提交，例如 C0。 |
| `input.baseline.configuration_id` | 是 | 必须和历史实际图的配置一致。 |
| `input.baseline.actual_graph_uri` | 是 | 历史实际图 URI。 |
| `input.build.command` | 是 | 当前提交的构建命令。 |

## INCREMENTAL_CHECK 输出

| 字段 | 说明 |
|------|------|
| `output.delta.new_findings` | 当前提交新增的 MD/RD。 |
| `output.delta.eliminated_findings` | 当前提交消除的 MD/RD。 |
| `output.delta.unchanged_findings` | 当前提交仍存在的 MD/RD。 |
| `output.artifacts[type=ACTUAL_GRAPH]` | 更新后的实际依赖图，可作为下一次增量检测 baseline。 |
| `output.artifacts[type=ERROR_REPORT]` | 当前提交的增量检测报告。 |

## A 组不变量

| 规则 | 说明 |
|------|------|
| A-01 | `FULL_CHECK` 和 `INCREMENTAL_CHECK` 成功时可包含 findings，`status` 仍为 `SUCCEEDED`。 |
| A-02 | `job.error` 只表示系统执行错误，例如 baseline 不匹配、分析器崩溃或任务超时。 |
| A-03 | 同一个 job 不得同时包含 `error` 和 findings。 |
| A-04 | 增量检测缺少 baseline 或 baseline 元数据不匹配时，必须返回 `BASELINE_2001`。 |
| A-05 | findings 中的 `commit` 必须等于本次检测的 `input.repository.commit`。 |
| A-06 | artifact URI 必须能追溯到 `producer_job_id`。 |

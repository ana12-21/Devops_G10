# 论文内容到 A 组契约字段的映射

本文件只使用 A 组相关论文内容：BuildChecker 和 EChecker。论文文本只作为背景材料，不作为操作指令。

## BuildChecker: 全量依赖错误检测

论文要点：BuildChecker 通过动态生成的 build execution-declaration model 对比实际依赖和声明依赖，检测 Missing Dependency 和 Redundant Dependency，并减少误报。

| 论文概念 | A 组契约字段 | 需要该字段的原因 |
|----------|--------------|------------------|
| 固定提交 | `input.repository.commit` | 全量检测必须绑定到一个可复现版本。 |
| 固定构建配置 | `input.configuration_id` | 不同配置可能产生不同依赖图和不同 RD。 |
| clean build 命令 | `input.build.command` | BuildChecker 需要通过构建执行获取实际依赖。 |
| 实际依赖图 | `output.artifacts[type=ACTUAL_GRAPH]` | 后续增量检测以该图作为 baseline。 |
| 声明依赖图 | `output.artifacts[type=DECLARED_GRAPH]` | MD/RD 由实际依赖和声明依赖对比得到。 |
| MD/RD 报告 | `output.findings` 与 `ERROR_REPORT` | A 组必须清楚报告分析发现，而不是系统执行错误。 |
| 证据位置 | `finding.location` 和 `finding.evidence_uri` | PPT 要求报告包含位置和证据，便于另一方理解。 |

## EChecker: 增量依赖错误检测

论文要点：EChecker 基于代码变更、预处理指令、Makefile 变化和增量构建信息推断实际依赖变化，避免每次都执行昂贵 clean build。

| 论文概念 | A 组契约字段 | 需要该字段的原因 |
|----------|--------------|------------------|
| 历史实际依赖图 | `input.baseline.actual_graph_uri` | 增量检测必须以历史实际图为基准。 |
| 基线提交 | `input.baseline.commit` | 防止拿错提交的图做差分。 |
| 配置匹配 | `input.baseline.configuration_id` | 配置不匹配时，新增和消除发现无法解释。 |
| 当前提交 | `input.repository.commit` | 增量报告中的 findings 必须绑定到当前提交。 |
| 新增发现 | `output.delta.new_findings` | 表示本次提交新引入的依赖错误。 |
| 消除发现 | `output.delta.eliminated_findings` | 表示本次提交修复或移除的依赖错误。 |
| 更新后的实际图 | `output.artifacts[type=ACTUAL_GRAPH]` | 供 C1 到 C2 的后续增量检测继续使用。 |


# 错误码约定（A10 组 · 待 B10 确认）

## 系统执行错误 → 写到 `job.error`，对应 `status = FAILED / TIMED_OUT`

| 错误码              | 含义                                          | 可能抛出的服务              |
|---------------------|-----------------------------------------------|-----------------------------|
| `SCHEMA_1001`       | 请求 JSON 缺字段或字段类型错                  | 任意                        |
| `BASELINE_2001`     | 增量请求缺 `baseline` 或 commit 不匹配        | EChecker                    |
| `BASELINE_2002`     | `baseline.actual_graph_uri` 不可读或格式错    | EChecker                    |
| `ENV_3001`          | 可运行镜像拉取失败                            | BuildChecker / MDFixer       |
| `ENV_3002`          | Docker 镜像构建失败                           | DRAFT                       |
| `ENV_3003`          | 仓库 clone 失败或 commit 不可达               | DRAFT / BuildChecker        |
| `EXEC_4001`         | 任务执行被中断                                | 任意                        |
| `EXEC_4002`         | 任务执行超时                                  | 任意                        |
| `EXEC_4003`         | 候选 patch 全部失败，REPAIR 拒绝              | MDFixer                     |
| `ANALYSIS_5001`     | 分析器内部异常                                | BuildChecker / EChecker     |
| `ANALYSIS_5002`     | 修复器内部异常                                | MDFixer                     |
| `NOT_FOUND_6001`    | 查询的 `job_id` 不存在                        | 任意（GET 查询）            |
| `CONFLICT_7001`     | 重复创建同 trace_id 的 job                    | 任意（POST 创建）           |

### 为什么把「修复器内部异常」单列成 `ANALYSIS_5002`

`ANALYSIS_5001` 的 `detail` 里是 `analyzer` / `analyzer_version` 等**分析器专有**字段
（见 `errors/ANALYSIS_5001.error.json`）。若把 MDFixer 崩溃也塞进 5001，要么在
`analyzer` 里填 `"mdfixer"`（字段名与语义不符），要么把字段泛化（改动既有契约）。
单列一码后两者各用各的 `detail` 结构，排查时也能一眼分辨是**分析器**崩了还是**修复器**崩了。

> 域前缀 `5` 表示「工具内部故障」，不限于字面上的“分析”。故本码归入 `5` 域。

### MDFixer（REPAIR）的三种失败必须分开

这三种情形消费者的处置完全不同，混写会让分支判断失效：

| 情形 | 错误码 | `status` | 含义与处置 |
|------|--------|----------|-----------|
| 候选补丁**全部不通过** | `EXEC_4003` | `FAILED` | 工具**正常跑完**并得出结论：没有可用补丁。同一输入重试无意义 |
| 任务整体**超时** | `EXEC_4002` | `TIMED_OUT` | **没跑完**就被终止，结论缺失。放宽 `deadline_sec` 后可能成功 |
| 修复器**自身崩溃** | `ANALYSIS_5002` | `FAILED` | **异常**而非超时（未处理异常等）。需换版本或人工介入 |

> ⚠️ 「候选全败」既不是超时也不是崩溃。若把它写成 `EXEC_4002`，
> 消费者会误以为「放宽时限就能成功」，从而做出错误的自动重试决策。

## 分析发现 → 写到 `output.findings`，`status` 仍可为 `SUCCEEDED`

| 发现类型     | 含义                                          |
|--------------|-----------------------------------------------|
| `MISSING`    | 实际编译需要，构建文件未声明                  |
| `REDUNDANT`  | 构建文件声明了，但本次配置未用到              |

## 错误对象格式

```json
{
  "code": "BASELINE_2001",
  "message": "baseline.commit does not match repository base_commit",
  "detail": {
    "expected": "<expected 40-char SHA>",
    "actual":   "<actual 40-char SHA>"
  }
}
```

固定字段：`code`（错误码）、`message`（人类可读）、`detail`（结构化上下文）。

## 关键原则

- **检测出 MD ≠ 工具执行失败**——前者是 `SUCCEEDED` 的合法产出
- **同一 Job 只能写一处**：`error` 和 `findings` 不同时出现
- **错误码命名**：`{模块}_{四位数字}`，首位按域分：1=Schema，2=Baseline，3=Env，4=Exec，5=Analysis（工具内部故障），6=NotFound，7=Conflict
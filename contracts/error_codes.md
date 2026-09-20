# 错误码约定（A10 组 · 待 B10 确认）

## 系统执行错误 → 写到 `job.error`，对应 `status = FAILED / TIMED_OUT`

| 错误码            | 含义                                  | 可能抛出的服务              |
|-------------------|---------------------------------------|-----------------------------|
| `SCHEMA_1001`     | 请求 JSON 缺字段或字段类型错          | 任意                        |
| `BASELINE_2001`   | 增量请求缺 baseline 或 commit 不匹配  | EChecker                    |
| `ENV_3002`        | Docker 镜像构建失败                   | DRAFT                       |
| `EXEC_4001`       | 任务执行被中断                        | 任意                        |
| `EXEC_4002`       | 任务执行超时                          | 任意                        |
| `ANALYSIS_5001`   | 分析器内部异常                        | BuildChecker / EChecker     |

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

## 关键原则

- **检测出 MD ≠ 工具执行失败**——前者是 SUCCEEDED 的合法产出
- **同一 Job 只能写一处**：`error` 和 `findings` 不同时出现
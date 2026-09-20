# 产物（Artifact）传递约定

## URI 格式

```
artifact://<pair_id>/<job_id>/<relative_path>
```

- `pair_id`: 配对组编号（我们用 `pair10`）
- `job_id`: 产生该产物的任务编号
- `relative_path`: 产物在工作区里的相对路径

## Artifact 元数据

每一份产物必须在 `output` 字段里给一个 URI，同时配套一份元数据：

```json
{
  "artifact_id": "graph-001",
  "type": "ACTUAL_GRAPH",
  "uri": "artifact://pair10/full01/actual.json",
  "media_type": "application/json",
  "producer_job_id": "job-full01",
  "sha256": "<可选，完整性校验时使用>"
}
```

## A 组产生的产物类型

| `type`           | 含义           | media_type           |
|------------------|----------------|----------------------|
| `ACTUAL_GRAPH`   | 实际依赖图     | application/json     |
| `DECLARED_GRAPH` | 声明依赖图     | application/json     |
| `MD_REPORT`      | 缺失依赖报告   | application/json     |
| `RD_REPORT`      | 冗余依赖报告   | application/json     |
| `BUILD_LOG`      | 构建日志       | text/plain           |

## B 组产生的产物类型（占位，待 B10 确认）

| `type`      | 含义                 | media_type       |
|-------------|----------------------|------------------|
| `DOCKERFILE`| 自动生成的 Dockerfile| text/dockerfile  |
| `IMAGE_REF` | 镜像引用             | text/plain       |
| `GIT_PATCH` | 修复补丁             | text/x-diff      |
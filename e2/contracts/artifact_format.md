# 产物（Artifact）传递约定

## URI 格式

```
artifact://<pair_id>/<job_id>/<relative_path>
```

- `pair_id`: 配对组编号（A/B 双组共用，我们用 `pair10`）
- `job_id`: 产生该产物的任务编号，**必须带 `job-` 前缀**
- `relative_path`: 产物在工作区里的相对路径

> ⚠️ **修订说明**：本文档早先的示例省略了 `job-` 前缀（形如 `.../pair10/full01/actual.json`），
> 与上面的模式串自相矛盾——`full01` 并不是一个合法的 `job_id`（真正的 `job_id` 是 `job-full01`）。
> 现已统一为 `.../pair10/job-full01/actual.json`，对应 B10 Issue 第 7 条。
> `task.schema.json` 的 `artifactUri` 模式串会强制这一点。
>
> 约定：`relative_path` 以 **`<job_id>/<filename>`** 开头，例如
> `artifact://pair10/job-draft01/Dockerfile`。同一 `job_id` 下的多个产物共享该前缀，
> 需要分层时再追加子目录（如 `.../job-full01/evidence/F-0001.json`）。

## Artifact 元数据

每一份产物必须在 `output.artifacts[]` 里给一条元数据记录（B10 Issue 第 4 条的目标形态）：

四类成功响应均以 `output.artifacts[]` 作为统一的产物入口；消费者按 `type`
查找对应记录，不再从 `output` 的裸字段读取产物。`IMAGE_REF` 记录的 `uri`
指向保存镜像引用字符串的文本产物，记录中的 `image_ref` 是该引用的示例值。
增量检查请求中的 `input.baseline.actual_graph_uri` 是历史产物的输入引用，继续保留。

```json
{
  "artifact_id": "actual-001",
  "type": "ACTUAL_GRAPH",
  "uri": "artifact://pair10/job-full01/actual.json",
  "media_type": "application/json",
  "producer_job_id": "job-full01",
  "sha256": "78535350a0c2be68f7e5fd8f52f12824443e8c33ab3b5ae3ae85f7250e2558e6"
}
```

### `sha256` 是必需字段

B10 Issue 第 6 条。此前标注为「可选，完整性校验时使用」，现提为**必需**，理由：

- 课程要求「必要时用 `sha256` 核验完整性」。若为可选，消费者每次消费前都要先探测
  「这次到底有没有哈希」，可复现性就变成了可选项；
- 成本极低——产物落盘后算一次哈希（一次字节流遍历）。

**为什么必需不会与「失败时无产物」冲突**：`artifacts[]` 只登记**已完整产出**的产物。
未完成或产出失败的产物**根本不进入数组**，所以不存在「有产物但无哈希可填」的情形。

| 项 | 约定 |
|----|------|
| 计算范围 | 产物**文件字节流**的全部内容（不做任何文本规范化，不剥 BOM，不含文件名与路径） |
| 编码形式 | 小写十六进制，固定 64 字符 |
| 校验时机 | 消费者在读取产物**之前**校验；不匹配即拒绝消费并报错，不得「先用后查」 |
| 失败产物 | 不登记进 `artifacts[]`；失败原因走 `job.error` |

### 样例中的 sha256 说明

样例不对应真实落盘的文件，因此其中的 `sha256` 按一条**可复现的约定**取：

```
sha256_sample = SHA-256(uri 字符串的 UTF-8 字节)
```

这样读者可以自行复算、核对格式与一致性：

```bash
python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" \
  "artifact://pair10/job-full01/actual.json"
# 78535350a0c2be68f7e5fd8f52f12824443e8c33ab3b5ae3ae85f7250e2558e6
```

**真实产物**必须按上表「计算范围」对产物文件本身计算，例如：

```bash
# Linux / macOS
sha256sum actual.json
# Windows
certutil -hashfile actual.json SHA256
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

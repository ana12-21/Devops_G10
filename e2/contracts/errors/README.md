# 系统执行错误详解（ENV_3002 / EXEC_4002 / ANALYSIS_5001）

> A10 组产出。这三个错误码是 E2 规范点名的**系统执行错误**，写入 `job.error`，
> 对应 `status = FAILED` / `TIMED_OUT`。**需与 B10 确认**（B 组同样会抛出其中部分）。
>
> 总览表见 `contracts/error_codes.md`；本文件补充**完整 JSON 结构与字段语义**。

## 1. 错误对象统一结构

所有 `job.error` 共用同一外壳，字段分三层：

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `code` | ✅ | string | `{域}_{四位}`，如 `ENV_3002` |
| `message` | ✅ | string | 人类可读描述，**禁止只写错误码** |
| `detail` | ⬜ | object | 结构化上下文，字段随错误码而定 |
| `phase` | ⬜ | enum | 失败所处阶段，见下表 |
| `retryable` | ⬜ | boolean | 重试是否有意义 |
| `occurred_at` | ⬜ | string | ISO8601 UTC，如 `2026-09-20T10:20:12Z` |

`phase` 取值：`VALIDATE` / `FETCH` / `ENV_PREPARE` / `BUILD` / `ANALYZE` / `REPORT` / `CLEANUP`

**最小合法形式**只有 `code` + `message`；`detail` 及以上均为可选，但推荐填全，
因为消费者（尤其 B 组 MDFixer）依赖 `detail` 判断能否重试、从哪一步恢复。

## 2. 三个错误码逐一详解

### 2.1 `ENV_3002` — 镜像构建失败

| 项 | 内容 |
|----|------|
| 含义 | 在准备可运行环境时，Docker 镜像构建失败 |
| 触发阶段 | `phase = ENV_PREPARE` |
| 典型抛出方 | DRAFT（主要）、BuildChecker（复用镜像时） |
| `retryable` | `true` — 外部依赖（网络、包源）问题重试可能成功 |
| 期望 `status` | `FAILED` |
| 与其他码的区分 | `ENV_3001` = 镜像**拉取**失败（已有镜像取不到）；`ENV_3003` = 仓库 clone / commit 不可达。**三者都是环境问题，但发生在不同步骤** |

```json
{
  "code": "ENV_3002",
  "message": "Docker image build failed: step 'RUN make' exited with code 2",
  "phase": "ENV_PREPARE",
  "retryable": true,
  "occurred_at": "2026-09-20T10:20:12Z",
  "detail": {
    "step": "RUN make",
    "dockerfile_line": 14,
    "exit_code": 2,
    "command": "make",
    "image_ref": "registry.local/pair10/draft02:sha-7f3a1c9",
    "build_log_uri": "artifact://pair10/job-full02/build.log",
    "failed_target": "src/main.o"
  }
}
```

`detail` 字段说明：

| 字段 | 说明 |
|------|------|
| `step` | 失败的 Dockerfile 指令原文 |
| `dockerfile_line` | 失败指令所在行号（便于直接定位） |
| `exit_code` | 该指令退出码，非 0 即失败 |
| `command` | 实际执行的构建命令 |
| `image_ref` | 失败时正在构建的镜像引用 |
| `build_log_uri` | 完整构建日志，**必填用于排查** |
| `failed_target` | 构建系统内部的失败目标（可选） |

**排查指引**：先看 `build_log_uri` 指向的日志尾部；若 `exit_code` 出现在 `apt-get`/`pip` 类指令上，
多为网络或包源问题（`retryable = true`）；若出现在 `RUN make` 上，说明是**代码本身编译不过**，
此时应改走 DRAFT 的迭代修复流程，而不是简单重试。

> ⚠️ 注意与检测发现的边界：`RUN make` 失败是 **ENV_3002 系统错误**；
> 而分析器报告"某依赖缺失"是 **MISSING 检测发现**（`status = SUCCEEDED`）。两者不可混淆。

### 2.2 `EXEC_4002` — 任务执行超时

| 项 | 内容 |
|----|------|
| 含义 | 任务在给定 `deadline_sec` 内未完成，被强制终止 |
| 触发阶段 | 任意阶段，通常是 `BUILD` 或 `ANALYZE` |
| 典型抛出方 | 任意服务 |
| `retryable` | `true` — 放宽 deadline 或提高并行度后可重试 |
| 期望 `status` | **`TIMED_OUT`**（不是 `FAILED`） |
| 与其他码的区分 | `EXEC_4001` = 被**主动中断**（用户取消）；`EXEC_4003` = 候选 patch 全部失败（**结论性失败**，重试无意义） |

```json
{
  "code": "EXEC_4002",
  "message": "job exceeded deadline of 600s and was terminated",
  "phase": "BUILD",
  "retryable": true,
  "occurred_at": "2026-09-20T12:10:00Z",
  "detail": {
    "deadline_sec": 600,
    "elapsed_sec": 604,
    "iterations_used": 3,
    "last_completed_step": "make src/parse.o",
    "attempt_log_uri": "artifact://pair10/job-repair02/attempt.log",
    "partial_output": false
  }
}
```

`detail` 字段说明：

| 字段 | 说明 |
|------|------|
| `deadline_sec` | 请求中给定的时限 |
| `elapsed_sec` | 实际耗时，应 ≥ `deadline_sec` |
| `iterations_used` | 已用迭代轮次（DRAFT / REPAIR 适用） |
| `last_completed_step` | 最后一个**成功完成**的步骤，供续跑定位 |
| `attempt_log_uri` | 超时前的部分日志 |
| `partial_output` | 是否已产出**可用**的部分结果。为 `false` 时消费者不得当作完整结论使用 |

> ⚠️ `partial_output = true` 才是危险情形：产物存在但可能不完整。
> 因此解析约定要求消费者在消费前用 `sha256` 核验，并在检查脚本中拒绝
> `TIMED_OUT` 且 `partial_output = false` 的文档携带 `output`。

### 2.3 `ANALYSIS_5001` — 分析器内部异常

| 项 | 内容 |
|----|------|
| 含义 | 环境与构建均正常，但**分析阶段**工具自身崩溃 |
| 触发阶段 | `phase = ANALYZE` |
| 典型抛出方 | BuildChecker / EChecker |
| `retryable` | `true` — 多为解析器对特定语法的兼容问题，换版本或降级策略可能成功 |
| 期望 `status` | `FAILED` |
| 与其他码的区分 | **本码最关键**：它表示"工具失败了"，与"工具成功发现了问题"（MISSING / REDUNDANT）**完全对立** |

```json
{
  "code": "ANALYSIS_5001",
  "message": "declared-dependency parser crashed while reading Makefile at line 41",
  "phase": "ANALYZE",
  "retryable": true,
  "occurred_at": "2026-09-20T10:21:12Z",
  "detail": {
    "analyzer": "makefile-parser",
    "analyzer_version": "0.9.3",
    "step": "parse_makefile",
    "file": "Makefile",
    "line": 41,
    "exit_code": 1,
    "partial_artifacts": [],
    "build_log_uri": "artifact://pair10/job-full02/build.log"
  }
}
```

`detail` 字段说明：

| 字段 | 说明 |
|------|------|
| `analyzer` | 崩溃的分析器名称 |
| `analyzer_version` | 版本号，便于复现与上报 |
| `step` | 崩溃所在内部步骤 |
| `file` / `line` | 触发崩溃的输入位置 |
| `exit_code` | 分析器进程退出码 |
| `partial_artifacts` | 崩溃前已落盘的产物 URI 列表。**空数组表示无任何可信产出** |
| `build_log_uri` | 构建阶段日志（构建本身已成功，用于确认问题出在分析而非构建） |

## 3. 关键边界：系统错误 vs 检测发现

这是 E2 最容易被误读的一点，因此单独列出对照：

| 情形 | `status` | `job.error` | `output.findings` | 含义 |
|------|----------|-------------|-------------------|------|
| 发现缺失依赖 | `SUCCEEDED` | 空 | 有（`MISSING`） | ✅ **工具正常完成** |
| 发现冗余依赖 | `SUCCEEDED` | 空 | 有（`REDUNDANT`） | ✅ **工具正常完成** |
| 分析器崩溃 | `FAILED` | `ANALYSIS_5001` | 空 | ❌ 工具失败，无可信结论 |
| 镜像构建失败 | `FAILED` | `ENV_3002` | 空 | ❌ 环境失败，未进入分析 |
| 任务超时 | `TIMED_OUT` | `EXEC_4002` | 空 | ❌ 未完成，结果不完整 |

三条不变量：

1. **`findings` 非空 ≠ 任务失败** —— 检测到 MD 是业务成果，`status` 仍为 `SUCCEEDED`。
2. **同一 Job 只能写一处** —— `job.error` 与 `output.findings` **互斥**。
3. **`error` 只在系统故障时出现** —— 绝不承载 `MISSING` / `REDUNDANT`。

落盘反例（应被拒绝）：`contracts/negative/error_and_findings.res.json`
正面样例（应被接受）：`contracts/md_report.sample.json`、`contracts/analysis_err.res.json`

## 4. 文件清单

| 文件 | 内容 |
|------|------|
| `ENV_3002.error.json` | 镜像构建失败的 `job.error` 纯对象 |
| `EXEC_4002.error.json` | 任务超时的 `job.error` 纯对象 |
| `ANALYSIS_5001.error.json` | 分析器崩溃的 `job.error` 纯对象 |
| `../error_codes.md` | 全部 12 个错误码总览表 |
| `../full_check_err.res.json` | `ENV_3002` 的完整任务响应样例 |
| `../repair_job_err.res.json` | `EXEC_4002` 的完整任务响应样例 |
| `../analysis_err.res.json` | `ANALYSIS_5001` 的完整任务响应样例 |

> 本目录的 `*.error.json` 是**可独立校验的纯错误对象**（即 `job.error` 的值本身），
> 便于消费方直接对错误结构做单元测试，无需构造整个 Job 文档。

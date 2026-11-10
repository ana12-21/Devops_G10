# ADR：集成接口决策

编号：ADR-E11-01　日期：2026-11-10　作者：241880335（A 轨道，G10 第 10 组）

## 问题

E11 要把 BuildChecker 的真实执行图接进 EChecker 的增量分析，E12 要把这条链路的产物通过异步任务 API 暴露出去。三个必须定下来的点：

1. 历史缓存里的 `actual` 应该来自 `strace` 真实图，还是 `gcc -MM` 静态推断？
2. 真实执行图与增量分析图目标集合不一致（前者含链接目标 `app`），在哪儿、怎么对齐？
3. 任务 API 的「产物」以什么为传递单位，如何保证消费方拿到的不是过期或篡改的报告？

## 候选方案

**方案 A（采用）**：基线取真实 `strace` 图，投影到对象目标后与 `gcc -MM` 交叉校验，不一致直接失败；产物以「相对路径 + SHA256」为传递单位，消费前强制校验 schema/commit/hash 三道闸。

**方案 B**：基线直接用 `gcc -MM`。省掉 `strace`，快、不需要 `SYS_PTRACE`，也不需要真实跑一次构建。

**方案 C**：基线取真实图，但不与 `gcc -MM` 交叉校验；两边发现不同时以真实图为准（毕竟"论文说的是真实执行"）。

**方案 D**：产物直接传 JSON 内容（内联在 envelope 的 `data` 里），不做文件级 URI 与哈希。

## 采用方案与原因

**采用 A**，理由分三点。

### 1. 为什么不用方案 B

论文的核心主张就是"从真实执行中学习依赖"。如果基线来自静态工具，那就绕开了要被验证的机制本身——E11 名义上"接入了 BuildChecker"，实际上只接了一个 `gcc` 调用，验收时的"BuildChecker 图接入历史缓存"这一条就成了空话。

代价是明确的：必须真的跑一次 `strace -ff` + `make -p`，需要 `SYS_PTRACE` 能力，单次耗时从毫秒级涨到百毫秒级。但基线只算一次，摊到后续所有增量分析上可以忽略。

### 2. 为什么不用方案 C

**只信真实图、不做交叉校验，等于放弃了唯一的错误检测手段。** 真实图也会错：`strace` 可能漏事件、进程归属可能算错、`make -p` 的解析可能撞上不支持的语法。如果真实图错了而没人发现，后续所有增量分析都会建立在错误基线上，而且因为"基线是真实执行的产物"这一身份，错误反而更难被怀疑。

`pipeline.execute()` 里那三行断言就是为此存在的：

```python
if projected != old['actual']:
    raise Failure('GRAPH_MISMATCH', 'BuildChecker baseline differs from GCC observations')
```

两条独立路径（动态 `strace` vs 静态 `gcc -MM`）对同一个项目给出相同结论，才允许继续。**这一条不是冗余，它是把"真实执行"这个主张变得可信的必要条件。**

### 3. 为什么不用方案 D

内联 JSON 的问题在于**没有内容身份**。消费方拿到一份 `incremental-check.json`，无法判断它是不是被中间环节改过、是不是被另一个提交的报告顶替了。

方案 A 的 `{uri, sha256, bytes}` 三元组让每个产物自带指纹：

- `uri` = `artifact://<job_id>/<相对路径>`，路径相对、不含绝对路径，可通过 `/v1/jobs/{id}/files/{rel}` 解析回原文件
- `sha256` = 内容哈希，消费前用 `load_artifact()` 重算比对，不符则 `ARTIFACT_HASH_MISMATCH`
- `bytes` = 长度，提供第二道粗校验

E12 实测中 85 个产物逐个下载并核对 `X-Content-SHA256`，85/85 一致。如果内联 JSON，这 85 次校验根本无从谈起。

## 输入输出字段

### envelope（所有阶段统一）

```json
{
  "schema_version": "e11e12-1",
  "job_id":  "job-<32 hex>",
  "trace_id": "trace-<32 hex>",
  "kind":    "full-check | incremental-check | fixed-md | repair | recheck | draft",
  "commit":  "<受测项目完整 SHA>",
  "status":  "SUCCEEDED",
  "data":    { ... },
  "artifacts": [ { "uri": "artifact://job-x/rel.json", "sha256": "<64 hex>", "bytes": 1234 } ]
}
```

`kind` 与 `commit` 是消费方最依赖的两个字段：前者防止"拿报告当补丁"，后者防止"拿旧提交的报告修新提交"。

### 请求（POST /v1/jobs）

```json
{ "idempotency_key": "<≤128 字符>",
  "input": { "mode": "e11-a|e11-b|e12", "repo": "/course/data/...",
             "base": "<40 hex>", "target": "<40 hex>",
             "candidate": "/course/data/...", "fixed_report": "/course/data/...",
             "expected_output": "1", "build_timeout": 600 } }
```

`repo` / `candidate` / `fixed_report` 三个路径字段**必须**落在 `/course/data` 之内，否则 400。这条限制不是形式主义：API 以容器内的 `/course` 为根，若允许任意路径，调用方就能读到仓库外的文件。

### 状态机

`QUEUED → RUNNING → SUCCEEDED | FAILED | TIMED_OUT`；服务重启时滞留的前两态改判为 `FAILED` 且 `error.code = SERVER_RESTARTED`。

## 兼容性与测试

### 与 E8–E10 的兼容

|对象|处理|
|---|---|
|`labs/e8e10/lab.py`|复用 `scan`/`patch`/`validate`，未改一行|
|`run_lab.py`|保留不动，与 `run_e11e12.py` 并存|
|`.github/workflows/e7-quality-gate.yml`|保留，未替换必需检查|
|新增 `.github/workflows/e11e12.yml`|独立 job `e11e12-integration`，不覆盖原规则数组|

E8–E10 的 `scan()` 输出 `schema_version = e8e10-1`，E11 层统一封装为 `e11e12-1`。两者不混用：`incremental-report.json` 保留 `e8e10-1` 原貌作为原始证据，`incremental-check.json` 才是带信封的交付物。这样既能追溯原始扫描结果，又能让下游按统一契约消费。

### 测试

|层级|内容|结果|
|---|---|---|
|契约单元测试|`test_contract.py` 10 项（原包）+ `StudentContracts` 3 项（本人新增）|13 tests OK|
|变异检验|去掉 `target` 过滤 / 只返回第一条 / 不排序|三处均失败，测试有效|
|STALE_REPORT 闸门|6 种构造输入（篡改 commit、跨目标消费、schema 不符、上游 FAILED、kind 不符）|全部按预期拒绝|
|E11-A 一致性|增量报告 vs `target-full` 全量报告（对象目标投影后）|一致|
|真实项目|C0→C1（只改函数体）两目标复用；C0→C2（改头文件）两目标刷新|均 SUCCEEDED，增量与全量一致|
|API HTTP 层|202/400/404/409、越界路径、幂等、重启恢复、`SERVER_RESTARTED`|全部符合|

### 我明确接受的局限

1. **`normalized()` 的比较范围是对象目标**。`app` 这类链接目标被丢弃。如果将来要检查链接目标的依赖错误，需要另加一层比较，不能复用这个函数。
2. **`key` 是全局的**。任一 `.c/.h` 的指令行变化会让**所有**目标一起刷新，没有 per-target 精细失效。真实项目目标数上千时这个代价会显著。
3. **`/course/data` 白名单只是路径前缀检查**，不做符号链接解析后的二次校验（`snapshot()` 里用 `resolve()` 之后没有再查一次）。当前的容器边界内风险有限，但如果 API 面向不可信调用方，这里需要加固。
4. **基线与目标必须同仓不同提交**。跨仓库比较不是接口设计的目标，`snapshot()` 对两者用同一个 `repo` 参数。

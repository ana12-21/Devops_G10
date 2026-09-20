# AI_USAGE

> 记录本次 E2 课堂中 AI 的建议、我们的判断、验证过程。

## 2026-09-20  E2 课堂契约设计

### 使用的 AI
- **CodeBuddy**（AI 编码助手）：辅助起草 JSON 样例、ADR / 契约文档骨架，并用于本地复核（`python scripts/validate.py --all` 实跑）
- 通用对话模型：用于接口取舍的方案讨论（六态状态机、error / findings 分离）

> 课程要求申报**实际使用**的工具，写法要与仓库里留下的执行痕迹一致；
> 不要把没用过的工具写上去，也不要漏掉真正用过的。

### 记录 1：统一任务模型
- **任务**：设计四类任务共用的 Job Schema
- **AI 提议**：`status` 用 `PENDING / ACTIVE / DONE` 三态
- **我们的判断**：改为 `QUEUED / RUNNING / SUCCEEDED / FAILED / TIMED_OUT / CANCELLED` 六态
- **理由**：课程 PPT 第 8 页规定六态；`PENDING` 与 HTTP `202 Accepted` 语义重叠
- **验证**：四类样例都能套用同一外壳
- **关联**：`contracts/task.schema.json`、`docs/ADR-001.md`

### 记录 2：系统错误 vs 分析发现
- **任务**：划清错误码与发现码
- **AI 提议**：把所有异常合并到 `job.error` 一个字段
- **我们的判断**：拆为 `job.error`（系统错误）与 `output.findings`（分析发现）
- **理由**：SUCCEEDED 状态也可能有 findings；不能让用户误以为 MD 是工具崩了
- **验证**：构造一个"只有 MD 没有系统错误"的样例，status=SUCCEEDED
- **关联**：`contracts/error_codes.md`

### 后续变更
- 2026-09-20（E3 阶段复核）：更正"使用的 AI"一栏，改为如实申报实际工具；E2 的契约内容本身未改动
- 2026-09-20（E3 阶段复核）：`data/commits.md` 的 T-006 占位已回填（C0/C1/C2 三个 40 位 SHA + 仓库地址）
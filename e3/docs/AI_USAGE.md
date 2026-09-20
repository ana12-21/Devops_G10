# AI_USAGE — E3 部分

> 记录本次 E3 课堂中 AI 的建议、我们的判断、验证过程。
> 模板继承自 `e2/docs/AI_USAGE.md`（E2 已有 2 条记录可参考）。
> 与 ADR-003、Backlog.md、practice_log.md 同步维护。

---

## 记录 1：E3 项目选定（合成 commit vs 真实开源项目）

- **任务**：决定 C0/C1/C2 三个 commit 的来源——用真实开源项目（如 fzy、clib、tcpdump）还是 A10 自构造的合成 commit？
- **AI 提议**：用真实开源项目，"更接近真实场景"。
- **我们的判断**：**拒绝**，改用合成 commit。
- **理由**：
  - 真实项目三步之间会掺杂无关 commit（修文档、CI、依赖升级），破坏"唯一变量"；
  - 真实项目 `HEAD` 不稳定，可能 force-push、删除分支；
  - E5/E8 工具需要"对照 oracle"做回归测试，真实项目会漂移。
- **验证**：`fixtures/commits/{C0,C1,C2}/` 用 `git init` + `git tag` 合成，每个目录附 `.git_info.txt`，两次复跑剔除 `ts` 后 stdout 完全一致（见 `work/reproducibility_rerun.log`）。
- **关联**：`docs/ADR-003.md` 决策 1；`docs/practice_log.md` 第一节；`docs/Backlog.md` T-105。

---

## 记录 2：E3 MD 报告撰写（如何"故意造" MD/RD 样本）

- **任务**：md-rd 样本的 Makefile 与 main.c 应该怎么写，才能让 MD + RD 同时出现？
- **AI 提议**：
  - 方案 A：写干净的 Makefile（`main.o: main.c config.h`），让 BuildChecker 跑出"无 findings"——"合规样本"。
  - 方案 B：在 Makefile 里**故意漏掉** config.h，**故意加上** unused.h，"双错制造成本"。
- **我们的判断**：**拒绝 A，采纳 B**——E3 是测试样本准备阶段，不是"展示工具完美运行"阶段。
- **理由**：
  - 方案 A 跑出来永远是空报告，没教学价值；
  - 方案 B 同时演示两种 finding（1 MISSING + 1 REDUNDANT），oracle.json 一次写齐，对 E5 工具的 finding parser 是更真实的压力测试。
- **验证**：`fixtures/md-rd/oracle.json` 含 2 条 finding（`provenance = INSTRUCTOR_ORACLE`）；跑两次后 md-rd 的 4 步观察全部符合 oracle（`work/20260920-135225/md-rd.observations.json`）。
- **关联**：`fixtures/md-rd/oracle.json`、`fixtures/md-rd/Makefile`、`docs/Backlog.md` T-101 / T-102。

---

## 记录 3：E3 RD 报告撰写（C2 实测偏差是否要"修正"）

- **任务**：C2 clean build 实测 = 12（PPT Slide 26 假设 = 19），要不要改源码让 PPT 假设成立？
- **AI 提议**：改 `config.h` 为 `#ifndef MODE ... #endif`，让命令行 `-DMODE=7` 起作用，clean build 输出 19，"严格对齐 PPT"。
- **我们的判断**：**拒绝**修改源码，保留 PPT 假设与实测的偏差。
- **理由**：
  - 保留 `config.h` 内 `#define MODE 0`（带末尾空格）才能演示"普通 make 时间戳检查漏掉命令变化"——这是 C2 的**唯一教学价值**；
  - 改 `#ifndef` 后 C2 退化成 C1（clean = 12，等同 C1），EChecker 在 C2 上跑不出"命令变化未触发重建"报警；
  - PPT Slide 26 备注其实已经说"普通 make 仍可能输出 12"，主表"clean = 19"是理想情况假设；我们实测更接近 PPT 备注。
- **验证**：GCC stderr `"MODE" redefined` 警告原文在 `work/20260920-135225/commit-C2.commands.json` 第 17 行；comparison_table.md 与 commit-C2.observations.json 同时注明差异；ADR-003 决策 3 是这条决策的正式归宿。
- **关联**：`docs/ADR-003.md` 决策 3；`docs/practice_log.md` 第二节第 3 条；`evidence/comparison_table.md`；`work/20260920-135225/commit-C2.observations.json`。

---

## 记录 4：E3 ADR-003 撰写（C0/C1/C2 决策的 ADR 风格）

- **任务**：写 ADR-003 时，结构应该照搬 E2 的 ADR-001/ADR-002 吗？还是 E3 这次有特殊模板？
- **AI 提议**：照搬 ADR-001 / ADR-002 的五段结构（Context / Decision / Alternatives / Consequences / Verification）。
- **我们的判断**：**采纳**，但 Verification 段加一个"复跑 PASS"的实测项（区别于 E2 ADR 只列决策项）。
- **理由**：
  - E2 的 ADR 是契约层面，没有 Verification 段（决策一旦做出，契约就能用）；
  - E3 ADR 必须证明"实测结果符合决策"，否则评审者无法判断决策是否落地；
  - 复用五段结构让 E2 → E3 → E5 的 ADR 阅读体验一致。
- **验证**：`docs/ADR-003.md` 末尾 Verification 表格列出 7 项检查（C0/C1/C2 clean、增量、stderr 警告、复跑一致性），全部 PASS 或按决策 3 标注 ⚠️。
- **关联**：`docs/ADR-003.md`；`e2/docs/ADR-001.md`；`e2/docs/ADR-002.md`。

---

## 模板（每次记录包含 5 个要素）

```markdown
### 记录 N：<任务名>
- **任务**：<要做什么>
- **AI 提议**：<AI 给的建议>
- **我们的判断**：<接受/拒绝/修改>
- **理由**：<为什么这样决定>
- **验证**：<怎么证明判断是对的>
- **关联**：<引用的文件路径>
```

**禁止**：
- 整段照搬 AI 内容而不验证
- 在无关联时伪造 commit SHA 或代码片段
- 在"判断"和"理由"段写空话（必须基于具体证据）

---

## 关联文档

- E2 的 AI_USAGE：`e2/docs/AI_USAGE.md`（格式参考、E2 的 2 条记录）
- E2 的 ADR-001：`e2/docs/ADR-001.md`（异步 Job 决策，E3 的 C0/C1/C2 Job 模型继承自此）
- E2 的 ADR-002：`e2/docs/ADR-002.md`（E3 EChecker finding 形态直接依赖此 ADR 的 error/findings 分离决策）
- E3 的 ADR-003：`e3/docs/ADR-003.md`（C0/C1/C2 设计决策 + C2 实测偏差）
- E3 的 Backlog：`e3/docs/Backlog.md`（T-101 ~ T-110 任务状态）
- E3 的 practice_log：`e3/docs/practice_log.md`（动手过程中的卡点、试错、决策时间线）
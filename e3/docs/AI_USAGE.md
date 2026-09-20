# AI_USAGE — E3 部分

> 记录本次 E3 课堂中 AI 的建议、我们的判断、验证过程。
> 模板继承自 `e2/docs/AI_USAGE.md`（E2 已有 2 条记录可参考）。
> 与 ADR-003、Backlog.md、practice_log.md 同步维护。

---

## 使用的 AI 工具（如实申报）

| 工具 | 用在哪 | 人做了什么 |
|------|--------|-----------|
| **CodeBuddy**（AI 编码助手） | 起草 `e3/scripts/run_lab.py`、`render_evidence.py`、`diff_reproducibility.py` 的初版；整理 evidence 与文档骨架；执行重跑并汇总数字 | 定样本设计、判定预期值、复核每一处数字与结论；所有命令都在本机 MinGW 实际跑过 |
| 通用对话模型（用于方案讨论） | 讨论"合成 commit vs 开源项目"、"MD/RD 怎么造"等取舍 | 采纳 / 拒绝的判断与理由记在下面的记录里 |

课程要求申报 AI 使用环节，这里如实写明：**AI 参与了脚本实现与文档整理，结论和预期值一律由组员人工判定并本地实测复核**。
工具名、路径等机器相关痕迹不写进证据文件（见记录 5）。

---

## 记录 1：E3 项目选定（合成 commit vs 真实开源项目）

- **任务**：决定 C0/C1/C2 三个 commit 的来源——用真实开源项目（如 fzy、clib、tcpdump）还是 A10 自构造的合成 commit？
- **AI 提议**：用真实开源项目，"更接近真实场景"。
- **我们的判断**：**拒绝**，改用合成 commit。
- **理由**：
  - 真实项目三步之间会掺杂无关 commit（修文档、CI、依赖升级），破坏"唯一变量"；
  - 真实项目 `HEAD` 不稳定，可能 force-push、删除分支；
  - E5/E8 工具需要"对照 oracle"做回归测试，真实项目会漂移。
- **验证**：`fixtures/commits/{C0,C1,C2}/` 用 `git init` + `git commit` + `git tag` 合成，每个目录附 `.git_info.txt`；固定提交时间后 SHA 可复现（任意机器重跑得到同一组 40 位哈希），两次复跑剔除 `ts` 后 stdout 完全一致（见 `work/reproducibility_diff.log`）。
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
- **验证**：`fixtures/md-rd/oracle.json` 含 2 条 finding（`provenance = INSTRUCTOR_ORACLE`）；跑两次后 md-rd 的 4 步观察全部符合 oracle（`work/20260920-144518/md-rd.observations.json`）。
- **关联**：`fixtures/md-rd/oracle.json`、`fixtures/md-rd/Makefile`、`docs/Backlog.md` T-101 / T-102。

---

## 记录 3：C2 实测偏差——先误判，后纠错

- **任务**：C2 clean build 实测 = 12（PPT Slide 26 预期 = 19），是改样本对齐 PPT，还是把 12 当成"实测偏差"记入 ADR？
- **AI 提议**：改 `config.h` 为 `#ifndef MODE ... #endif`，让命令行 `-DMODE=7` 起作用，clean build 输出 19，"严格对齐 PPT"。
- **我们的判断（第一轮）**：**拒绝修改源码**，理由是"保留 `config.h` 内 `#define MODE 0` 才能演示普通 make 漏掉命令变化"。
- **第一轮验证暴露的问题**：复核证据时发现，旧样本下 **C2 的增量输出与 clean 输出都是 12**。两个答案相同，"make 没重编"和"重编了但结果碰巧一样"在证据上分不开——**等于证明不了"命令变化被漏检"**，C2 的检测价值反而被抹掉了。
- **我们的判断（第二轮，纠正）**：**采纳 AI 的第一轮提议**。`config.h` 加 `#ifndef` 守卫，并把 C2 场景改成按真实迁移执行（C1 命令构建 → 换 C2 命令跑普通 make → 再 clean）。
- **纠错理由**：
  - `config.h` 自己的注释写着 "MODE=0 is the default; C2 will override this via Makefile CFLAGS"——**原意就是让命令行宏生效**，是样本实现写错了，不是平台差异；
  - 修正后增量 12 / clean 19，两个答案不同，"命令变化被漏检"才有直接证据，且与 PPT Slide 26-27 一致；
  - 把它记成"实测偏差"会让下游误以为需要新增 `MACRO_OVERRIDE` 这类 finding——那是被错误样本带出来的假需求。
- **验证**：`work/20260920-144518/commit-C2.commands.json` 第 4 步 make 的 stdout 只有 `gcc main.o -o main`（没有 `gcc -c`），第 7 步 clean 构建才有 `-DMODE=7`；两条输出分别是 `BASE=10 FEATURE=2 MODE=0`（12）与 `BASE=10 FEATURE=2 MODE=7`（19）。见 `evidence/build_c2.txt`。
- **关联**：`docs/ADR-003.md` 决策 3（修订版）+ §修订记录；`docs/practice_log.md` 第二节第 3 条；`evidence/comparison_table.md`。

---

## 记录 4：E3 ADR-003 撰写（C0/C1/C2 决策的 ADR 风格）

- **任务**：写 ADR-003 时，结构应该照搬 E2 的 ADR-001/ADR-002 吗？还是 E3 这次有特殊模板？
- **AI 提议**：照搬 ADR-001 / ADR-002 的五段结构（Context / Decision / Alternatives / Consequences / Verification）。
- **我们的判断**：**采纳**，但 Verification 段加"复跑 PASS"的实测项，并额外加一段 §修订记录。
- **理由**：
  - E2 的 ADR 是契约层面，没有 Verification 段（决策一旦做出，契约就能用）；
  - E3 ADR 必须证明"实测结果符合决策"，否则评审者无法判断决策是否落地；
  - 决策 3 被修订过，如果不留修订记录，读到的就是"一个从没被质疑过的决策"，反而掩盖了纠错过程。
- **验证**：`docs/ADR-003.md` 末尾 Verification 表列出 10 项检查（C0/C1/C2 clean、增量、增量≠clean、clean 走真实 recipe、路径相对化、复跑一致性等），全部 ✅。
- **关联**：`docs/ADR-003.md`；`e2/docs/ADR-001.md`；`e2/docs/ADR-002.md`。

---

## 记录 5：复核阶段——证据文件本身的三处工程缺陷

- **任务**：交付前复核"别人能不能照着重跑一遍"。
- **AI 提议**：只检查内容对不对，路径与生成方式不影响结论。
- **我们的判断**：**拒绝**。发现三处缺陷并全部修复（登记为 T-114 ~ T-116）：
  1. **证据里混进本机绝对路径**（`C:\Users\...\Devops_G10\...`）→ 别的机器复跑必然对不上；改为记录相对仓库根的路径；
  2. **`make clean` 没走 Makefile 配方**：早期把 `clean` 短路成 Python 删文件，因为当时 PATH 里没有 POSIX shell（缺少 `sh`，recipe 里的 `rm` 无法执行）。改为把 Git for Windows 的 `usr/bin` 加进子进程 PATH，让 make 真正执行 `rm -f`；只有确实没有 shell 时才回退，并在记录里写 `note` 标明是回退路径；
  3. **`.git_info.txt` 的 SHA 不可复现**：提交时间取的是运行时的时间，换台机器重跑 SHA 就变了，Slide 5 的"保存真实 SHA"名不副实；改为固定 `COMMIT_DATES`，并让回填逻辑能覆盖旧的 `sha` 行。
- **理由**：这三处都不是"结论对不对"的问题，而是"证据能不能被独立验证"的问题——评审者要拿 SHA 去 checkout、要照路径去复跑，任何一处名不副实，整套 evidence 的可信度都要打折。
- **验证**：仓库内 `git grep` 不到本机绝对路径；`evidence/build_*.txt` 里 `make clean` 的 stdout 是真正的 `rm -f main.o main`；三次独立重跑，C0/C1/C2 的 SHA 完全一致。
- **关联**：`docs/Backlog.md` T-114 ~ T-116；`scripts/render_evidence.py`；`evidence/env_check.txt`。

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
- 申报 AI 使用时不写工具名、或与实际使用的工具不一致

---

## 关联文档

- E2 的 AI_USAGE：`e2/docs/AI_USAGE.md`（格式参考、E2 的 2 条记录）
- E2 的 ADR-001：`e2/docs/ADR-001.md`（异步 Job 决策，E3 的 C0/C1/C2 Job 模型继承自此）
- E2 的 ADR-002：`e2/docs/ADR-002.md`（E3 EChecker finding 形态直接依赖此 ADR 的 error/findings 分离决策）
- E3 的 ADR-003：`e3/docs/ADR-003.md`（C0/C1/C2 设计决策）
- E3 的 Backlog：`e3/docs/Backlog.md`（T-101 ~ T-116 任务状态）
- E3 的 practice_log：`e3/docs/practice_log.md`（动手过程中的卡点、试错、决策时间线）

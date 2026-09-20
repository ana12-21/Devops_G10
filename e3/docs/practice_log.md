# E3 实践日志（A10 组）

> Backlog T-110 + README 第六节"提交要求"中的"卡在哪里、试过什么、下一步"产物。
> 时间：2026-09-20 苏州课堂 E3 阶段。
> 与 E2 阶段的 `e2/docs/practice_log.md`（A10 ↔ B10 配对三轮）不重叠，本文件聚焦 E3 内部样本准备过程的卡点、试错与决策。

---

## 一、动手前的问题与决策

### 1. C0/C1/C2 用真项目还是合成项目？

- **试过的方案**：先查 BuildChecker 论文里用的开源项目（fzy / clib / ck / tcpdump），看能否找到三步 commit 序列。
- **遇到的问题**：外部项目三步之间往往掺杂无关 commit（修文档、CI 配置、依赖升级），无法保证"唯一变量"；而且外部仓库随时可能 force-push，SHA 不稳定。
- **最终决策**：合成 commit。详见 `docs/ADR-003.md` 决策 1。

### 2. md-rd 样本要不要"故意造" MD/RD？

- **试过的方案**：第一版 `Makefile` 写成 `main.o: main.c config.h`（无 MD/RD），想让 BuildChecker 跑出"无 findings"——但这样样本没有教学价值。
- **最终决策**：故意在 `Makefile` 里只声明 `unused.h`，故意在 `main.c` 里 `#include "config.h"`，让 MD + RD 同时出现，对应到 oracle.json 的 2 条 finding。

---

## 二、跑 `scripts/run_lab.py` 时的卡点

### 1. 首次跑 `make` 时 cc 命令不存在

- **现象**：Windows 默认无 `cc`，只有 `gcc`。
- **排查路径**：`gcc --version` 可用 → Makefile 把 `CC` 改为 `gcc`。
- **试过的方案 A**：直接在 Makefile 里写死 `gcc` → 失去跨平台性。
- **最终决策**：Makefile 用 `CC ?= cc`（默认 cc），调用方传 `CC=gcc` 或在 Makefile 注释说明 Windows 需用 mingw32-make。详见 `fixtures/md-rd/Makefile` 头部注释。

### 2. 第一次跑 md-rd 时，app.exe 不会自动加后缀

- **现象**：`./app` 在 Windows 下找不到文件，实际是 `app.exe`。
- **排查路径**：`make app` 后 `ls` 看到 `app.exe`。
- **最终决策**：`scripts/run_lab.py` 探测 `.exe` 后缀，`cmd` 字段写抽象的 `app`，`actual_cmd` 写相对仓库根的真实文件（如 `e3/work/<ts>/md-rd/app.exe`）。**不写绝对路径**——证据要能在另一台机器上照着复跑，本机安装位置不该进仓库。复跑日志见 `work/20260920-144518/md-rd.commands.json`。

### 3. C2 跑出来不是 PPT 预期的 19，而是 12

- **现象**：C2 的 Makefile 把 `CFLAGS` 改成 `-O0 -Wall -DMODE=7`，clean build 后 stdout 还是 `BASE=10 FEATURE=2 MODE=0`，不是 PPT Slide 26 的 19。
- **第一反应**：是不是 `scripts/run_lab.py` 错了？
- **排查路径**：
  1. 查 `commit-C2.commands.json` 的 stderr：`"MODE" redefined`，指出 `config.h` 内的 `#define MODE 0` 与命令行 `-DMODE=7` 冲突；
  2. 查 GCC 手册：源文件里的 `#define` 会覆盖命令行 `-D`，所以 `-DMODE=7` 根本到不了编译结果；
  3. 回看 `config.h` 自己的注释："MODE=0 is the default; C2 will override this via Makefile CFLAGS"——**原意就是要让命令行宏生效**，说明是样本写错了，不是平台差异。
- **试过的方案 A**：不动样本，把"实测 12"当成"实测优于 PPT 假设"写进 ADR（原 ADR-003 决策 3）。**复核时发现致命问题**：那样 C2 的增量输出和 clean 输出**都是 12**，两个答案一样，等于无法证明"make 漏掉了命令变化"——"make 没重编"和"重编了但结果碰巧相同"在证据上分不开。样本的检测价值被抹掉了。放弃。
- **试过的方案 B**：换 Linux + GCC 跑 → 本机无 Linux 容器；而且这本来就不是平台问题，换平台也一样是 12。放弃。
- **最终决策**：
  1. `config.h` 的 `MODE` 加 `#ifndef` 守卫，让 `-DMODE=7` 真正生效；
  2. C2 场景改成**按真实迁移执行**：先用 C1 的 Makefile 构建出"变更前"的 `main.o`，再换入 C2 的 Makefile 跑普通 `make`（观察它只重链接、不重编），最后 `make clean && make` 拿到 19；
  3. 证据文本改为由 `scripts/render_evidence.py` 从 JSON 生成，不再手工抄写。
- **结果**：增量 **12** / clean **19**，与 PPT Slide 26-27 完全一致；增量与 clean 的差异本身就是"命令变化被漏检"的直接证据。详见 `docs/ADR-003.md` 决策 3（修订版）。

### 4. `make clean` 一度没走 Makefile 的配方

- **现象**：Makefile 里写的是 `clean: rm -f main.o main`，但早期记录中 `make clean` 的 stdout 是脚本自己拼的字符串，不是 make 的实际输出。
- **排查路径**：GNU make 在 Windows 上若 PATH 里找不到 POSIX shell（`sh.exe`），recipe 会交给 cmd.exe，`rm` 命令不存在 → `make clean` 直接失败。当时的应对是把 `clean` 短路成 Python 的 `os.remove` 绕过去——绕过去之后，"clean 构建"这一步就不再是 make 的行为，证据也就名不副实。
- **最终决策**：把 Git for Windows 自带的 `usr/bin`（内含 `sh.exe`、`rm.exe`）加进**子进程**的 PATH，`make clean` 就能真正执行 `rm -f`；只有在确实找不到 shell 时才回退到直接删文件，并在记录里写 `note` 说明这是回退路径，不会被误读成 make 的输出。现在 `evidence/build_*.txt` 里 `make clean` 的 stdout 是真正的 `rm -f main.o main`。

### 5. `.git_info.txt` 里的 SHA 换台机器就对不上

- **现象**：合成 commit 用 `git commit` 生成，提交时间取的是当时的时间，因此 SHA 每次重跑都不一样——写进 `.git_info.txt` 的"真实 SHA"只能在生成它的那台机器、那一次运行里成立。
- **最终决策**：给三个合成 commit 固定作者/提交时间（`run_lab.py` 的 `COMMIT_DATES`），并让回填逻辑可以覆盖已有的 `sha =` 行。现在任意机器重跑都得到同一组 40 位 SHA，`git checkout <sha>` 可独立验证，Slide 5 要求的"保存真实 SHA"才真正落地。

---

## 三、reproducibility 验证

### 1. 第二次跑 `python scripts/run_lab.py` 时，第一次的 work 目录要保留

- **要求**：PPT Slide 16 "每次新建目录，保留旧证据"。
- **实施**：`run_lab.py` 用 `_now()` 生成新时间戳目录，目录已存在时直接报错退出，绝不覆盖。
- **验证**：跑完两次后 `work/` 下有两个目录 `20260920-144512/` 和 `20260920-144518/`，互不覆盖。

### 2. 两次跑输出是否完全一致？

- **方法**：`scripts/diff_reproducibility.py` 对比两个目录的 `*.observations.json` 与 `*.commands.json`——剔除 `ts` 字段、把时间戳目录名归一为 `<TS>`，再逐字节比对。
- **结果**：`OVERALL: PASS (8 files checked)`，4 个 observations 文件 + 4 个 commands 文件全部一致。
- **落痕**：`work/reproducibility_diff.log`（比对报告）、`work/reproducibility_rerun.log`（第二次运行的完整输出）。
- **为什么这次可信**：证据里的路径全部相对仓库根，比对结果只取决于工具链版本，不取决于仓库放在哪儿。

---

## 四、与 B10 的对接（A10 ↔ B10 在 E3 阶段）

### E3 阶段 B10 的责任范围（由 README 划分）

- B10 提供 `fixtures/draft/` 下的 DRAFT 样本（main.c / Makefile / README.md）。
- B10 提供 `fixtures/draft/Dockerfile.broken` 作为失败候选。
- A10 不消费 draft 样本，只在 E5 阶段会用 DRAFT 产物。

### 当前 `fixtures/draft/` 状态

- 仅有 `.gitkeep`，B10 尚未提交实际样本。
- A10 不阻塞：E3 阶段 A10 的 `build_c{0,1,2}.txt` 与 md-rd 实验不依赖 draft。

### 待办

- 等 B10 推 draft 样本 → 在本文件增补一节记录对接过程。
- 如 B10 提交延期，A10 的 E5 评估不影响，因为 BuildChecker / EChecker 不消费 DRAFT 产物。

---

## 五、当前卡点 / 试过什么 / 下一步

### 已完成的清单（与 README 第七节"验收清单"对照）

- ✅ `fixtures/md-rd/` 完整
- ✅ `oracle.json` 含 1 MISSING + 1 REDUNDANT
- ✅ `evidence/build_md-rd.txt`（MD 漏重建 → clean 生效 → RD 多余编译三步）
- ✅ `fixtures/commits/{C0,C1,C2}/.git_info.txt`（真实 tag + 可复现 SHA）
- ✅ `evidence/build_c{0,1,2}.txt`
- ✅ `evidence/env_check.txt`（OS / CPU / git / make / gcc / python 版本 + recipe shell 可用性）
- ✅ `evidence/comparison_table.md`
- ✅ `docs/ADR-003.md`
- ✅ `docs/Backlog.md`
- ✅ `docs/AI_USAGE.md`
- ✅ `docs/practice_log.md`（本文件）

### 遗留 / 下一步

- ➖ `evidence/linux-verified/` —— 本机无 Linux 容器，**不阻塞** E3 验收（T-108）
- ⚠️ 与 B10 的 E3 阶段对接记录 —— 等 B10 提交 draft 后补一节
- ➖ C2 的 `MACRO_OVERRIDE` finding —— 决策 3 修订后样本里不再存在宏覆盖，这一类发现已无必要（T-112 保留登记，以免后人重复提出）

### 不阻塞 E3 的项（明确放弃本次不做）

- ❌ 用 Linux + GCC 复现 C2 —— 已不需要：Windows + MinGW 上 C2 clean 就是 19
- ❌ `scripts/run_lab.py` 加 `--cross-platform` 开关（T-111）
- ❌ `task.schema.json` 加 `MACRO_OVERRIDE` 枚举（T-112，已失效）

---

## 六、状态机讨论（继承自 E2 practice_log，E3 视角）

E3 的 evidence 全部走 SUCCEEDED 路径：

```
QUEUED ──► RUNNING ──► SUCCEEDED  (md-rd / C0/C1/C2 全程无 FAILED)
```

唯一需要关注的是**任务自身 SUCCEEDED 但发现 ≠ 0**——这正是 ADR-002 抛出的语义边界，E3 的 evidence 完整演示了这条边界：

| 场景 | status | findings | 工具态度 |
|------|--------|----------|----------|
| md-rd 首次 build | SUCCEEDED | 无 | 正常产物 |
| md-rd 改 config.h 后漏重建 | SUCCEEDED | 无（普通 make 没发现） | **漏检样本**——EChecker 应在此报警 |
| md-rd clean 后输出 2 | SUCCEEDED | 无 | 正常产物 |
| md-rd 改 unused.h 触发 cc -c | SUCCEEDED | 无（普通 make 没发现） | **漏检样本**——EChecker 应在此报警 |
| C0/C1 clean | SUCCEEDED | 无 | 正常产物 |
| C2 增量（12） | SUCCEEDED | 无（普通 make 没发现） | **漏检样本**——EChecker 应在"命令变化未触发重建"上报警 |
| C2 clean（19） | SUCCEEDED | 无 | 正常产物（全量构建拾取新命令） |

→ A 后续 EChecker 必须能识别"任务 SUCCEEDED 但漏检"的三种情况：MD、RD、命令变化未触发重建。

---

## 七、时间线

| 时间 | 事件 |
|------|------|
| 2026-09-20 上午 | E2 阶段交付（契约 / ADR / Backlog / validate.py 全绿） |
| 2026-09-20 13:47 | 首次跑 `scripts/run_lab.py` → `work/20260920-134753/` |
| 2026-09-20 13:52 | 复跑 `scripts/run_lab.py` → `work/20260920-135225/` |
| 2026-09-20 13:53 | reproducibility 验证 PASS，剔除 ts 后一致 |
| 2026-09-20 14:00 | 发现 C2 实测 12 ≠ PPT 19，写入 ADR-003 + comparison_table.md |
| 2026-09-20 14:13 | commit bcab888：补齐 docs/* 与 evidence/* |
| 2026-09-20 14:40 | 复核发现 C2 增量与 clean 输出相同 → 样本无法证明"命令变化被漏检"；同时发现证据里混入了本机绝对路径、`make clean` 没走真实配方、SHA 不可复现 |
| 2026-09-20 14:41 | 修订 `config.h`（`#ifndef MODE` 守卫）；C2 场景改为按真实迁移执行；`clean` 改为真跑 make 配方；路径改为相对仓库根；固定提交时间使 SHA 可复现 |
| 2026-09-20 14:45 | 重跑两次 → `work/20260920-144512/`、`work/20260920-144518/`；`OVERALL: PASS (8 files checked)`；C2 增量 12 / clean 19，与 PPT 一致 |
| 2026-09-20 14:50 | 新增 `scripts/render_evidence.py`，证据文本改由 JSON 生成；补齐 `evidence/env_check.txt`；更新 ADR-003 / 本文件 / Backlog / README |

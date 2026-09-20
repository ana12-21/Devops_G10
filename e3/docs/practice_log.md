# E3 实践日志（A10 组）

> Backlog T-110 + README 第六节"提交要求"中的"卡在哪里、试过什么、下一步"产物。
> 时间：2026-09-20 苏州课堂 E3 阶段。
> 与 E2 阶段的 `e2/docs/practice_log.md`（A10 ↔ B10 配对三轮）不重叠，本文件聚焦 E3 内部样本准备过程的卡点、试错与决策。

---

## 一、动手前的问题与决策

### 1. C0/C1/C2 用真项目还是合成项目？

- **试过的方案**：先查 BuildChecker 论文里用的开源项目（fzy / clib / ck / tcpdump），看能否找到三步 commit 序列。
- **遇到的问题**：外部项目三步之间往往掺杂无关 commit（修文档、CI 配置、依赖升级），无法保证"唯一变量"。
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
- **最终决策**：`scripts/run_lab.py` 在调用可执行文件时探测 `.exe` 后缀，把 `cmd` 字段写成抽象的 `app`，但 `actual_cmd` 字段写真实路径。复跑日志见 `work/20260920-135225/md-rd.commands.json`。

### 3. C2 跑出来不是 PPT 预期的 19，而是 12

- **现象**：C2 Makefile 改了 `CFLAGS = -O0 -Wall -DMODE=7`，clean build 后 stdout 还是 `BASE=10 FEATURE=2 MODE=0`，不是预期的 19。
- **第一反应**：是不是 `scripts/run_lab.py` 错了？
- **排查路径**：
  1. 查 `commit-C2.commands.json` 第 17 行 stderr：`"MODE" redefined`，提示 config.h 内 `#define MODE 0` 与命令行 `-DMODE=7` 冲突。
  2. 看 GCC 文档：源文件内的 `#define` 默认会覆盖命令行 `-D`。
  3. 看 PPT Slide 26 备注："普通 make 仍可能输出 12"——其实 PPT 已经**预期**了这个偏差，但 Slide 26 主表里又写 "clean = 19"。
- **试过的方案 A**：把 `config.h` 改成 `#ifndef MODE` 包裹，让命令行宏起作用 → 失去 C2 的"命令变化未触发重建"教学意义（C2 退化成 C1）。
- **试过的方案 B**：换 Linux + GCC 跑 → 本机无 Linux 容器。
- **最终决策**：保留 `config.h` 硬编码，把偏差写到 ADR-003 + comparison_table.md。详见 `docs/ADR-003.md` 决策 3。

---

## 三、reproducibility 验证

### 1. 第二次跑 `python scripts/run_lab.py` 时，第一次的 work 目录要保留

- **要求**：PPT Slide 16 "每次新建目录，保留旧证据"。
- **实施**：`scripts/run_lab.py` 第 6 步用 `_now()` 生成新时间戳目录，绝不覆盖。
- **验证**：跑完两次后 `work/` 下有两个目录 `20260920-134753/` 和 `20260920-135225/`，互不覆盖。

### 2. 两次跑输出是否完全一致？

- **方法**：写一个小脚本对比两个目录的 `*.observations.json` 与 `*.commands.json`，剔除 `ts` 字段后做字符串 diff。
- **结果**：4 个 observations 文件 + 4 个 commands 文件 全部一致。
- **落痕**：`work/reproducibility_rerun.log`。

---

## 四、与 B10 的对接（A10 ↔ B10 在 E3 阶段）

### E3 阶段 B10 的责任范围（由 README 划分）

- B10 提供 `fixtures/draft/` 下的 DRAFT 样本（main.c / Makefile / README.md）。
- B10 提供 `fixtures/draft/Dockerfile.broken` 作为失败候选。
- A10 不消费 draft 样本，只在 E5 阶段会用 DRAFT 产物。

### 当前 `fixtures/draft/` 状态

- 仅有 `.gitkeep`，B10 尚未提交实际样本。
- A10 不阻塞：E3 阶段 A10 的 build_c{0,1,2}.txt 与 md-rd 实验不依赖 draft。

### 待办

- 等 B10 推 draft 样本 → 在 practice_log.md 增补一节记录对接过程。
- 如 B10 提交延期，A10 的 E5 评估不影响，因为 BuildChecker / EChecker 不消费 DRAFT 产物。

---

## 五、当前卡点 / 试过什么 / 下一步

### 已完成的清单（与 README 第七节"验收清单"对照）

- ✅ `fixtures/md-rd/` 完整
- ✅ `oracle.json` 含 1 MISSING + 1 REDUNDANT
- ✅ `evidence/build_md_unbuilt.txt` / `build_md_clean.txt` / `build_rd_unused.txt`
- ✅ `fixtures/commits/{C0,C1,C2}/.git_info.txt`
- ✅ `evidence/build_c{0,1,2}.txt`
- ✅ `evidence/comparison_table.md`
- ✅ `docs/ADR-003.md`
- ✅ `docs/Backlog.md`
- ✅ `docs/AI_USAGE.md`
- ✅ `docs/practice_log.md`（本文件）

### 遗留 / 下一步

- ➖ `evidence/linux-verified/` ——本机无 Linux 容器，**不阻塞** E3 验收
- ⚠️ `evidence/env_check.txt` ——本机 GCC / make / python 版本记录，T-113 已登记备查
- ⚠️ 与 B10 的 E3 阶段对接记录 ——等 B10 提交 draft 后补一节
- ⚠️ C2 偏差在 E5 EChecker 工具里的识别 ——需新增 `MACRO_OVERRIDE` finding 类型，T-112 已登记备查

### 不阻塞 E3 的项（明确放弃本次不做）

- ❌ 重新跑 Linux GCC 复现 C2 = 19 的环境假设
- ❌ `scripts/run_lab.py` 加 `--cross-platform` 开关（T-111）
- ❌ `task.schema.json` 加 `MACRO_OVERRIDE` 枚举（T-112，需 E5 决定）

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
| C2 clean (实测 12) | SUCCEEDED | 无 | **MACRO_OVERRIDE 候选**——T-112 |

→ A 后续 EChecker 必须能识别"任务 SUCCEEDED 但漏检 MD/RD/MACRO_OVERRIDE"三种情况。

---

## 七、时间线

| 时间 | 事件 |
|------|------|
| 2026-09-20 上午 | E2 阶段交付（契约 / ADR / Backlog / validate.py 全绿） |
| 2026-09-20 13:47 | 首次跑 `scripts/run_lab.py` → `work/20260920-134753/` |
| 2026-09-20 13:52 | 复跑 `scripts/run_lab.py` → `work/20260920-135225/` |
| 2026-09-20 13:53 | reproducibility 验证 PASS，剔除 ts 后完全一致 |
| 2026-09-20 14:00 | 发现 C2 偏差，写入 ADR-003 + comparison_table.md |
| 2026-09-20 14:30 | 补齐 docs/* 与 evidence/*（本文件 + ADR-003 + Backlog.md + AI_USAGE.md + 8 份 evidence） |
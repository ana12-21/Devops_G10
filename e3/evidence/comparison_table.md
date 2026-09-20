# C0/C1/C2 增量 vs Clean 对照表

> 来源：PPT Slide 27（E3 / 28）"备查：A 组步骤 10：比较增量与全量"
> 数据：`python scripts/run_lab.py` 落盘 → `work/20260920-144518/`
> 复跑对照：与 `work/20260920-144512/` 剔除 `ts` 后逐字段比对 PASS（见 `work/reproducibility_diff.log`）
> 本表的 stdout 原文由 `scripts/render_evidence.py` 从 `work/<ts>/*.json` 生成，见 `evidence/build_c{0,1,2}.txt`。

## PPT Slide 27 要求的对照矩阵

| 版本 | 变更内容 | 人工预期发现 | 普通 make（增量） | clean build | 与 PPT 预期 |
|------|----------|--------------|-------------------|-------------|-------------|
| C0 | 声明正确的初始提交 | 无 MD/RD | — | `BASE=10 MODE=0`（**10**） | ✅ clean=10 匹配 |
| C1 | `main.c` 新增 `#include "feature.h"`，Makefile 未同步宣告 | MD：`main.o` 缺 `feature.h` 依赖（oracle: MISSING） | — | `BASE=10 FEATURE=2 MODE=0`（**12**） | ✅ clean=12 匹配 |
| C2 | 源码与 C1 逐字节相同，只把 `CFLAGS` 从 `-O0 -Wall` 改为 `-O0 -Wall -DMODE=7` | 命令变化：普通 make 不重编译 → 漏检 | `BASE=10 FEATURE=2 MODE=0`（**12**） | `BASE=10 FEATURE=2 MODE=7`（**19**） | ✅ 增量=12 / clean=19 均匹配 |

## C2 的关键证据链

`work/20260920-144518/commit-C2.commands.json` 记录了完整的迁移过程：

| # | 动作 | make 的 stdout | 程序输出 |
|---|------|----------------|----------|
| 1-3 | 用 **C1 的 Makefile** 构建 C2 源码（变更前状态） | `gcc -O0 -Wall -c main.c -o main.o` / `gcc main.o -o main` | `BASE=10 FEATURE=2 MODE=0` → **12** |
| 4-5 | 换入 **C2 的 Makefile**（只改命令），普通 `make` | `gcc main.o -o main` ← **只重链接，没有 `-c`** | `BASE=10 FEATURE=2 MODE=0` → **12（漏检）** |
| 6-8 | `make clean` 后再 `make` | `rm -f main.o main` / `gcc -O0 -Wall -DMODE=7 -c main.c -o main.o` | `BASE=10 FEATURE=2 MODE=7` → **19（全量构建才发现）** |

要点（对应 PPT Slide 26 备注"普通 make 仍可能输出 12"）：

1. **普通 make 的时间戳规则看不见命令变化**——`main.o` 的依赖 `main.c` / `config.h` 逐字节未变且比 `main.o` 旧，所以第 4 步只重链接，`gcc -c` 一次都没跑。
2. **只有 clean build 才拾取新命令**，所以增量和全量给出 12 / 19 两个不同的答案——这正是 EChecker 必须报警的场景。
3. 反过来说：**增量与 clean 输出相同，就无法证明"make 漏掉了命令变化"**。第一版样本的 `config.h` 用了裸 `#define MODE 0`，`-DMODE=7` 被源码内的宏覆盖，增量与 clean 都是 12，两个答案一样、看不出漏捡与否，已按 ADR-003 决策 3（修订版）改回 `#ifndef MODE` 守卫。

## Make 时间戳检查在 C2 的行为（与 Slide 26 对照）

第 4 步 stdout 只有 `gcc main.o -o main`，没有 `gcc -c`：印证 Slide 26 "Make 的普通时间戳检查可能漏掉命令变化"。EChecker 可以据此在"任务 SUCCEEDED 但产物与声明的编译命令不一致"时报警。

## Reproducibility 验证

两次跑 `work/20260920-144512/` 与 `work/20260920-144518/`，剔除 `ts` 字段并把时间戳目录名归一为 `<TS>` 后：

| 文件 | 结果 |
|------|------|
| `md-rd.commands.json` / `md-rd.observations.json` | PASS |
| `commit-C0/C1/C2.commands.json` | PASS |
| `commit-C0/C1/C2.observations.json` | PASS |

`OVERALL: PASS (8 files checked)`，原始日志见 `work/reproducibility_diff.log`。

另外，`fixtures/commits/{C0,C1,C2}` 的合成 commit 使用固定提交时间（`run_lab.py` 的 `COMMIT_DATES`），因此 `.git_info.txt` 里记录的 40 位 SHA 在任意机器上重跑都一致、可独立 checkout 验证（PPT Slide 5 "保存真实 SHA"）。复跑日志见 `work/reproducibility_rerun.log`。

## Slide 10 相互检查自检

- 别人能按 README 运行吗：✅ `python scripts/run_lab.py` 即可重跑；证据里的路径全部相对仓库根，不含本机绝对路径
- 人工答案和实际日志分清了吗：✅ `fixtures/md-rd/oracle.json`（人工，`INSTRUCTOR_ORACLE`） vs `work/<时间>/*.observations.json`（实测）
- 预期结果能说明依据吗：✅ oracle 来源 = `fixtures/md-rd/oracle.json` 的 `provenance` 字段；C0/C1/C2 的依据 = PPT Slide 24-27 的预期表
- 失败记录能定位到具体版本吗：✅ 本轮无失败；合成样本的 provenance（`INSTRUCTOR_SYNTHESIZED`）与真实 tag/SHA 记在各自的 `.git_info.txt`

## 跨文档引用

- 单场景完整 stdout/stderr：`evidence/build_md-rd.txt`、`evidence/build_c{0,1,2}.txt`
- 原始机读证据：`work/20260920-144518/*.json`
- 环境与工具版本：`evidence/env_check.txt`
- 设计决策：`docs/ADR-003.md`（决策 3 = C2 样本修订，决策 4 = 证据由脚本生成）
- 任务状态：`docs/Backlog.md` T-105 ~ T-107
- 动手卡点：`docs/practice_log.md` 第二节第 3 条

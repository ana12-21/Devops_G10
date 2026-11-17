# B 组项目的 A 组适配说明

## 来源

| 项 | 值 |
| --- | --- |
| 上游仓库 | https://github.com/Richardo11chen/Devops_B10 |
| 上游路径 | `e3/fixtures/mdfixer` |
| 上游 base 提交 | `f6b826805ed07ad19c5e4960793170dad6f45d53` |
| 上游 target 提交 | `29d0cb7435994e7b6476d351b857f9bb14a2dffb` |
| target 提交的实际改动 | 新增 `extra.h`，并在 `main.c` 顶部加入 `#include "extra.h"` |

## 为什么需要适配

A 组 BuildChecker / EChecker 采用的 E8-E10 teaching profile 有硬性约束：

1. 项目编译单元必须恰好是 `main.c` 与 `helper.c`；
2. 必须存在 `config.h`；
3. `Makefile` 必须为 `main.o` 和 `helper.o` 给出**显式**规则；
4. `CFLAGS` 必须属于 `-O0` / `-O1` / `-O0 -DMODE=1`；
5. 构建入口固定为 `make app`，且容器必须能从 `./app` 启动。

B 组原项目只满足第 2 条。按 E13 手册要求，先用**原样代码**运行得到 `UNSUPPORTED_PROJECT`
（证据：`work/e13-c1/out-unsupported/`），再在隔离副本中做最小适配后重跑。

## 适配内容（4 项，全部在 base 提交完成）

| # | 文件 | 改动 | 对应约束 |
| --- | --- | --- | --- |
| 1 | `helper.c` | 新增，提供 `int helper(void){return 0;}` | 1 |
| 2 | `Makefile` | `CFLAGS = -I.` → `CFLAGS = -O0` | 4 |
| 3 | `Makefile` | `app` 由伪目标改为**真实产物**（`main.o` + `helper.o` 链接成 `app`），`main` 保留为别名，新增 `helper.o` 规则，`clean` 增加 `helper.o` | 3、5 |
| 4 | `Dockerfile.broken` | COPY 清单补 `helper.c`、`RUN make main` → `RUN make app`、`CMD ["./main"]` → `CMD ["./app"]` | 5 |

### 第 3、4 项的来由（两次失败记录）

1. 第一次尝试沿用 B 组原 `Dockerfile.broken`（`COPY main.c extra.h config.h Makefile ./`、
   `CMD ["./main"]`），候选下载入 `helper.c` 后校验报
   `Candidate changed required project/build/runtime instructions`
   → 证据见 `work/e13-c1-a-tests-b-attempt1-EXECUTION_FAILED/`。
2. 第二次把 `Dockerfile.broken` 对齐，但 `Makefile` 里 `app` 只是 `app: main` 伪目标，
   `make app` 只产出 `./main`；DRAFT 用 `./app` 启动时报
   `exec: "./app": stat ./app: no such file or directory`（verify 退出码 127）
   → 证据见 `work/e13-c1-a-tests-b-attempt2-EXEC_FAIL127/`。
3. 第三次把 `app` 改为真实产物后通过。

## 明确没有改动的内容

- `main.c`：base 与 target 两版均保持 B 组原文，`printf("%s\n", MESSAGE)` 未动，**程序输出仍为 `v1`**。
- `config.h`：保持 `#define MESSAGE "v1"` 原文。
- `extra.h`：target 提交引入，内容为 B 组原文。
- `Makefile.implicit`、`md_report.json`、`reference.patch`、`README.md`、`.lab-project.json`：原样保留。

## 预期缺陷（MD）

`Makefile` 中声明 `main.o: main.c`，而编译 `main.c` 时 gcc 会读取 `config.h`；
target 提交再加 `extra.h`。因此：

- base 提交：`main.o` 缺 `config.h`；
- target 提交：`main.o` 缺 `config.h`、`extra.h`。

这正是待检测、待修复的 Makefile 依赖缺陷（MD），与 B 组 target 提交的设计意图一致。

## 预期程序输出

`v1`（不是课程样例的 `1`）。这是 B 组 `config.h` 的 `MESSAGE` 决定的，适配未改动它，
请求文件因此使用 `"expected_output": "v1"`。

## 执行者说明

B 组同学未参与本次运行。上述适配与后续运行由 A 组（学号 241880335）完成，
适配决策与原始不支持项记录在 E13 交叉测试记录中，**不构成独立交叉验证**。

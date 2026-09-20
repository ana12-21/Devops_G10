# Backlog（A10 组 · E3 阶段）

> Backlog T-110 产物：T-101 ~ T-110 E3 任务实际状态。
> 状态字段：✅ 完成 ｜ ⚠️ 部分完成 / 有偏差 ｜ ❌ 未做 ｜ ➖ 不在 A10 范围
> 与 `e3/README.md` 第五节"实验流程"一一对应。

| ID     | 任务                                       | 责任方 | 产物                                                                 | 验收条件                                                                   | 状态 |
|--------|--------------------------------------------|--------|----------------------------------------------------------------------|----------------------------------------------------------------------------|------|
| T-101  | 选定 1 个 MD 样本项目，写 `fixtures/md-rd/` | A 组   | `fixtures/md-rd/{main.c,config.h,unused.h,Makefile}`                 | 完整可跑的小项目                                                           | ✅ |
| T-102  | 写人工答案 `fixtures/md-rd/oracle.json`    | A 组   | `fixtures/md-rd/oracle.json`                                        | `provenance = INSTRUCTOR_ORACLE`，含 1 MISSING + 1 REDUNDANT                | ✅ |
| T-103  | 验证 MD 现象：改头文件不重建，clean 才生效 | A 组   | `evidence/build_md_unbuilt.txt`、`evidence/build_md_clean.txt`        | 改 `config.h` 后 `make` 仍输出旧值；clean build 后输出新值                | ✅ |
| T-104  | 验证 RD 现象：改 unused 头触发多余 cc      | A 组   | `evidence/build_rd_unused.txt`                                       | 改 `unused.h` 注释后 `make` 触发 `cc -c main.c -o main.o`                  | ✅ |
| T-105  | git tag C0（声明正确）→ C1（新增 include）→ C2（只改命令） | A 组   | `fixtures/commits/{C0,C1,C2}/.git_info.txt`                          | 三处都有真实 tag + SHA                                                     | ✅ |
| T-106  | 在每个 commit 上跑增量 + clean build       | A 组   | `evidence/build_c0.txt`、`build_c1.txt`、`build_c2.txt`              | 每份含 clean + 增量两条构建线 + 完整 stdout/stderr                          | ✅ |
| T-107  | 写对照表 `evidence/comparison_table.md`    | A 组   | `evidence/comparison_table.md`                                       | C0/C1/C2 增量 vs clean 矩阵完整 + C2 偏差根因                              | ✅ |
| T-108  | 在 Linux 跑 strace，记录 config.h 访问       | A 组   | `evidence/linux-verified/`                                           | strace 显示 `openat("config.h" ...) === 3`（若环境允许）                    | ➖ 本机无 Linux 容器，留为可选 |
| T-109  | 撰写 ADR-003（C0/C1/C2 设计决策）           | A 组   | `docs/ADR-003.md`                                                    | 含 context/decision/alternatives/consequences/verification                | ✅ |
| T-110  | 撰写 AI_USAGE（E3 部分）+ 补充 Backlog + practice_log | A 组   | `docs/AI_USAGE.md`、`docs/Backlog.md`、`docs/practice_log.md`         | 4 个章节齐全，每条记录含 5 要素（任务/AI 提议/判断/理由/验证）            | ✅ |

## 衍生 backlog（E3 结束前不强制，登记备查）

| ID      | 任务                                          | 备注                                                                 |
|---------|-----------------------------------------------|---------------------------------------------------------------------|
| T-111   | `run_lab.py` 加 `--cross-platform` 标志切换 MinGW / Linux 行为 | C2 偏差在不同平台可能不同，工具需可重跑 |
| T-112   | `task.schema.json` 的 `findings.type` 增 `MACRO_OVERRIDE` 候选 | C2 偏差识别需求，E5 阶段决定是否启用 |
| T-113   | `evidence/env_check.txt` 记录本机 GCC / make / python 版本     | 与 ADR-003 决策 3 的"Verification"对应，本次先补                     |

## 与 E2 Backlog 的关系

E2 Backlog（`e2/docs/Backlog.md`）T-001 ~ T-010 是契约设计阶段，已全部完成或占位完成。
E3 Backlog（T-101 ~ T-110）是样本准备阶段，与 E2 不重叠，但消费 E2 的契约：

| E3 任务 | 消费的 E2 产物 |
|---------|----------------|
| T-101 ~ T-104 | `contracts/task.schema.json`、`contracts/error_codes.md`、`contracts/artifact_format.md` |
| T-105 ~ T-107 | （无直接消费，EChecker 内部模型继承自 ADR-001） |
| T-108 ~ T-110 | ADR-001（异步 Job 模式）、ADR-002（error/findings 分离） |

## 状态总结

- **A10 完成度**：T-101 ~ T-107、T-109、T-110 共 9 项 ✅；T-108 ➖；无 ❌
- **总进度**：10 / 11 = 91%（去除可选项）
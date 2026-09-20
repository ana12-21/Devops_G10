# Backlog（A10 组 · E3 阶段）

> Backlog T-110 产物：T-101 ~ T-110 E3 任务实际状态。
> 状态字段：✅ 完成 ｜ ⚠️ 部分完成 / 有偏差 ｜ ❌ 未做 ｜ ➖ 不在 A10 范围
> 与 `e3/README.md` 第五节"实验流程"一一对应。

| ID     | 任务                                       | 责任方 | 产物                                                                 | 验收条件                                                                   | 状态 |
|--------|--------------------------------------------|--------|----------------------------------------------------------------------|----------------------------------------------------------------------------|------|
| T-101  | 选定 1 个 MD 样本项目，写 `fixtures/md-rd/` | A 组   | `fixtures/md-rd/{main.c,config.h,unused.h,Makefile}`                 | 完整可跑的小项目                                                           | ✅ |
| T-102  | 写人工答案 `fixtures/md-rd/oracle.json`    | A 组   | `fixtures/md-rd/oracle.json`                                        | `provenance = INSTRUCTOR_ORACLE`，含 1 MISSING + 1 REDUNDANT                | ✅ |
| T-103  | 验证 MD 现象：改头文件不重建，clean 才生效 | A 组   | `evidence/build_md-rd.txt`                                           | 改 `config.h` 后 `make` 仍输出旧值；clean build 后输出新值                | ✅ |
| T-104  | 验证 RD 现象：改 unused 头触发多余 cc      | A 组   | `evidence/build_md-rd.txt`                                           | 改 `unused.h` 注释后 `make` 触发 `gcc -c main.c -o main.o`                  | ✅ |
| T-105  | git tag C0（声明正确）→ C1（新增 include）→ C2（只改命令） | A 组   | `fixtures/commits/{C0,C1,C2}/.git_info.txt`                          | 三处都有真实 tag + SHA，且 SHA 可复现、可独立 checkout                     | ✅ |
| T-106  | 在每个 commit 上跑增量 + clean build       | A 组   | `evidence/build_c0.txt`、`build_c1.txt`、`build_c2.txt`              | 每份含 clean + 增量两条构建线 + 完整 stdout/stderr                          | ✅ |
| T-107  | 写对照表 `evidence/comparison_table.md`    | A 组   | `evidence/comparison_table.md`                                       | C0/C1/C2 增量 vs clean 矩阵完整，C2 增量(12) ≠ clean(19) 有原始证据          | ✅ |
| T-108  | 在 Linux 跑 strace，记录 config.h 访问       | A 组   | `evidence/linux-verified/`                                           | strace 显示 `openat("config.h" ...) === 3`（若环境允许）                    | ➖ 本机无 Linux 容器，留为可选 |
| T-109  | 撰写 ADR-003（C0/C1/C2 设计决策）           | A 组   | `docs/ADR-003.md`                                                    | 含 context/decision/alternatives/consequences/verification                | ✅ |
| T-110  | 撰写 AI_USAGE（E3 部分）+ 补充 Backlog + practice_log | A 组   | `docs/AI_USAGE.md`、`docs/Backlog.md`、`docs/practice_log.md`         | 4 个章节齐全，每条记录含 5 要素（任务/AI 提议/判断/理由/验证）            | ✅ |

## 复核阶段新增任务（T-114 ~ T-116）

出题复核时发现三处证据自身的缺陷，均已修复：

| ID     | 任务                                             | 产物                                                                 | 验收条件                                                             | 状态 |
|--------|--------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------|------|
| T-114  | 证据文本改为由脚本从 JSON 生成，不再手工抄写       | `scripts/render_evidence.py`、`evidence/build_*.txt`                   | 改样本 → 重跑 → 重新生成，三份数据（JSON/文本/对照表）不会互相打架   | ✅ |
| T-115  | 固定合成 commit 的作者/提交时间，使 SHA 可复现      | `run_lab.py` 的 `COMMIT_DATES`、`.git_info.txt` 的 `sha` 行             | 任意机器重跑得到同一组 40 位 SHA，可 `git checkout` 验证              | ✅ |
| T-116  | 证据中的路径改为相对仓库根，去掉本机绝对路径        | `run_lab.py` 的 `_rel()`、`work/<ts>/*.json`、`evidence/env_check.txt`  | 仓库内不含本机绝对路径，换机器复跑比对结果不变                        | ✅ |

## 衍生 backlog（E3 结束前不强制，登记备查）

| ID      | 任务                                          | 备注                                                                 |
|---------|-----------------------------------------------|---------------------------------------------------------------------|
| T-111   | `run_lab.py` 加 `--cross-platform` 标志切换 MinGW / Linux 行为 | 本次不做；C2 已在 MinGW 上复现 PPT 数值，跨平台开关仅是便利性 |
| T-112   | ~~`task.schema.json` 的 `findings.type` 增 `MACRO_OVERRIDE` 候选~~ | **已失效**：该需求来自"源码内宏覆盖命令行宏"的错误样本，ADR-003 决策 3 修订后样本里不再存在宏覆盖。保留登记，以免后人重复提出 |
| T-113   | `evidence/env_check.txt` 记录本机 GCC / make / python 版本     | ✅ 已补齐（含 OS / CPU / 各工具版本 / recipe shell 可用性） |

## 与 E2 Backlog 的关系

E2 Backlog（`e2/docs/Backlog.md`）T-001 ~ T-010 是契约设计阶段，已全部完成或占位完成。
E3 Backlog（T-101 ~ T-110）是样本准备阶段，与 E2 不重叠，但消费 E2 的契约：

| E3 任务 | 消费的 E2 产物 |
|---------|----------------|
| T-101 ~ T-104 | `contracts/task.schema.json`、`contracts/error_codes.md`、`contracts/artifact_format.md` |
| T-105 ~ T-107 | （无直接消费，EChecker 内部模型继承自 ADR-001） |
| T-108 ~ T-110 | ADR-001（异步 Job 模式）、ADR-002（error/findings 分离） |

## 状态总结

- **A10 完成度**：T-101 ~ T-107、T-109、T-110 共 9 项 ✅；T-113 ~ T-116 复核阶段新增 4 项 ✅；T-108 ➖；无 ❌
- **总进度**：13 / 14 = 93%（去除可选项 T-108）

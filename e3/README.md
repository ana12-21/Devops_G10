# E3 — 软件演化与维护实验

> 教学实验 E3：6 个开源项目的演化分析（MD/RD）
> 教师：吕骏 ｜ 助教：曾星伟
> 日期：2026-09-20 起

## 实验目标

为每个被分析项目产出**两次文档**：

| 文档 | 全称 | 触发时机 | 关键字段 |
|------|------|----------|----------|
| **MD** | Mutation Documentation | 项目第一次 commit（**C1**） | 改动原因 + 改动方式 + 改前/改后代码段 |
| **RD** | Regression Documentation | 后续 commit（**C2**） | bug 触发条件 + 错误信息 + 修复 commit |

## 被分析的 6 个开源项目

| # | 项目 | GitHub URL | C0 SHA | C1 SHA | C2 SHA |
|---|------|------------|--------|--------|--------|
| 1 | generic-c-library | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |
| 2 | sds                | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |
| 3 | fzy                | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |
| 4 | jsmn               | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |
| 5 | pwnat              | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |
| 6 | zlib               | `<TODO>` | `<TODO>` | `<TODO>` | `<TODO>` |

> SHA 待 `e3/commits/<project>.json` 填写。

## 目录结构

```text
e3/
├── README.md                          ← 本文件（E3 总览）
│
├── md_samples/                        ← 6 份 MD 报告样例
│   ├── 01_generic-c-library.md
│   ├── 02_sds.md
│   ├── 03_fzy.md
│   ├── 04_jsmn.md
│   ├── 05_pwnat.md
│   └── 06_zlib.md
│
├── commits/                           ← C0/C1/C2 元数据
│   ├── 01_generic-c-library.json
│   ├── 02_sds.json
│   └── ...
│
├── evidence/                          ← 命令执行日志
│   ├── build_log_<project>.txt
│   └── diff_<project>_<c1>_<c2>.txt
│
└── docs/                              ← E3 自己的文档
    ├── ADR-002.md                     # 软件维护策略决策
    ├── Backlog.md                     # T-101~T-110 E3 任务表
    ├── AI_USAGE.md                    # AI 使用记录（E3 部分）
    └── practice_log.md                # E3 实践日志
```

## 实验流程（Backlog 摘要）

| 阶段 | 任务 | 产物 |
|------|------|------|
| T-101 | 选定 6 个项目 + 记录 C0/C1/C2 | `e3/commits/*.json` |
| T-102 | 每个项目克隆 + 验证可构建 | `e3/evidence/build_log_*.txt` |
| T-103 | 为每个 C1 commit 写一份 MD | `e3/md_samples/*.md` |
| T-104 | 为每个 C2 commit 写一份 RD | `e3/md_samples/*_RD.md` |
| T-105 | 用 git diff 生成对比 | `e3/evidence/diff_*.txt` |
| T-106 | 撰写 ADR-002（维护策略） | `e3/docs/ADR-002.md` |
| T-107 | 撰写 AI_USAGE（E3 部分） | `e3/docs/AI_USAGE.md` |
| T-108 | 与 A 组（A10）校对契约 | `e3/docs/practice_log.md` |

## 与 E2 的关系

E2 完成了**契约设计**（Job 模型、错误码、URI 格式）。
E3 在 E2 基础上做**项目演化分析**——不直接调用 E2 服务，但参考 E2 文档格式（ADR、Backlog、AI_USAGE）保持一致风格。

## 验收清单（E3）

- [ ] 6 个项目的 C0/C1/C2 完整 SHA 已记录
- [ ] 6 份 MD 报告齐全（每份含改前/改后代码段）
- [ ] 6 份 RD 报告齐全（每份含触发条件 + 错误信息）
- [ ] ADR-002 / Backlog / AI_USAGE / practice_log 四份文档齐全
- [ ] 每个项目至少一次成功的 build_log（可在 evidence/ 中追溯）
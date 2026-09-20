# E2 — 需求与接口契约设计


## 角色

| 组别  | 服务                   | 职责                       |
|-------|------------------------|----------------------------|
| A10   | BuildChecker + EChecker | 依赖检测（**本仓库**）       |
| B10   | DRAFT + MDFixer         | 环境生成与修复（配对组）    |

## 仓库用途

E2 课堂契约交付物：

- `contracts/` — 四类任务的请求 / 响应 / 错误 / 产物样例
- `data/` — C0/C1/C2 的 40 位 SHA 与仓库地址（已回填）
- `docs/` — ADR、Backlog、AI 使用记录、配对练习
- `scripts/` — 契约校验脚本 `validate.py`

## 详细结构

```text
e2/
├── README.md                          ← 本文件
├── contracts/                         # 契约样例（E2 主交付物）
│   ├── task.schema.json              # Job 统一模型（4 类 × 6 态）
│   ├── artifact_format.md            # 产物 URI 规范
│   ├── error_codes.md                # 12 类错误码 + 命名约定
│   ├── dockerfile_job.{req,res,_err.res}.json      # DRAFT 三件套
│   ├── full_check.{req,res,_err.res}.json          # FULL_CHECK 三件套
│   ├── incremental_check.{req,res}.json            # INCREMENTAL_CHECK 两件套
│   ├── repair_job.{req,res,_err.res}.json          # REPAIR 三件套
│   └── query_job.{req,res}.json                    # GET 查询两件套
├── docs/
│   ├── ADR-001.md                    # 异步 Job 模式决策
│   ├── Backlog.md                    # T-001~T-010 任务表
│   ├── AI_USAGE.md                   # AI 建议使用记录
│   └── practice_log.md               # T-009 A10↔B10 三轮配对记录
├── data/
│   └── commits.md                    # T-006：C0/C1/C2 完整 SHA + 仓库地址 + 取得方式
└── scripts/
    └── validate.py                   # 契约校验脚本（--all / --negative）
```


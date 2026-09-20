# DevOps 教学实验 E2 - Pair10 · A 组

> **需求与接口契约设计**
> 教师：吕骏 ｜ 助教：曾星伟

## 仓库用途

E2 课堂契约交付物：

- `contracts/` — 四类任务的请求 / 响应 / 错误 / 产物样例
- `docs/` — ADR、Backlog、AI 使用记录

## 角色

| 组别  | 服务                  | 职责                  |
|-------|-----------------------|-----------------------|
| A10   | BuildChecker + EChecker | 依赖检测（本次仓库）|
| B10   | DRAFT + MDFixer         | 环境生成与修复（配对组）|

## 账号信息

- 秦林炜
- GitHub：[ana12-21](https://github.com/ana12-21)
- 邮箱：221900015@smail.nju.edu.com 3353794280@qq.com

## 文件结构

```text
.
├── README.md
├── contracts/                                       # 契约样例（E2 主交付物）
│   ├── task.schema.json                            # Job 统一模型（4 类 × 6 态）
│   ├── artifact_format.md                          # 产物 URI 规范
│   ├── error_codes.md                              # 12 类错误码 + 命名约定
│   ├── dockerfile_job.{req,res,_err.res}.json      # DRAFT 三件套
│   ├── full_check.{req,res,_err.res}.json          # FULL_CHECK 三件套
│   ├── incremental_check.{req,res}.json            # INCREMENTAL_CHECK 两件套
│   ├── repair_job.{req,res,_err.res}.json          # REPAIR 三件套
│   └── query_job.{req,res}.json                    # GET 查询两件套
├── docs/
│   ├── ADR-001.md                                  # 异步 Job 模式决策
│   ├── Backlog.md                                  # T-001~T-010 任务表
│   ├── AI_USAGE.md                                 # AI 建议使用记录
│   └── practice_log.md                             # T-009 A10↔B10 三轮配对记录
├── data/
│   └── commits.md                                  # T-006 数据占位（E3 待补 SHA）
└── scripts/
    └── validate.py                                 # 契约校验脚本（--all / --negative）
```

> 备注：`{req,res,_err.res}` 表示同名前缀 + 三种扩展名的并列写法（shell brace expansion），实际仓库中以三条独立文件存在。

## 选定的分析项目（待填写）

- 仓库地址：`<OWNER>/<PROJECT>`（GitHub URL）
- C0 完整 SHA：`<40 位>`
- C1 完整 SHA：`<40 位>`
- C2 完整 SHA：`<40 位>`

## 配对组

- B10 仓库：`<待填写>`
- B10 GitHub：`<待填写>`

## 验收清单

- [ ] `task.schema.json` 在 validate.py 下通过
- [ ] 6 个 JSON 样例字段完整
- [ ] 错误码至少覆盖 6 类
- [ ] ADR / Backlog / AI_USAGE 三份文档齐全
- [ ] 与 B10 组在 PR / Issue 上互相确认契约
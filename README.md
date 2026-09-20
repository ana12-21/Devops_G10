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

## 文件结构

```
.
├── README.md
├── contracts/
│   ├── task.schema.json
│   ├── full_check.req.json
│   ├── full_check.res.json
│   ├── full_check_err.res.json
│   ├── incremental_check.req.json
│   ├── incremental_check.res.json
│   ├── error_codes.md
│   └── artifact_format.md
└── docs/
    ├── ADR-001.md
    ├── Backlog.md
    └── AI_USAGE.md
```

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
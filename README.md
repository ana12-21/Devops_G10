# DevOps G10 教学实验仓库

> 南京大学苏州校区 2026 秋季 · DevOps 课程 · 10A 组

## 仓库用途


每个实验独立成子目录，互不干扰：

```
DevOps_G10/
├── README.md                       ← 本文件（仓库总览）
│
├── e2/                             ← 实验 2（已完成）
│   ├── README.md                   ← E2 总览
│   ├── contracts/  data/  docs/  scripts/
│
└── e3/                             ← 实验 3（进行中）
    ├── README.md                   ← E3 总览
    ├── md_samples/  commits/  evidence/  docs/
```

## 实验清单

| 实验  | 标题                  | 状态      | 详情                       |
|-------|-----------------------|-----------|----------------------------|
| **E2** | 需求与接口契约设计    | ✅ 已完成 | [`e2/README.md`](e2/README.md) |
| **E3** | 软件演化与维护实验    | 🟡 进行中 | [`e3/README.md`](e3/README.md) |

## 角色

| 组别 | 服务                   | 职责                       |
|------|------------------------|----------------------------|
| A10  | BuildChecker + EChecker | 依赖检测（**本仓库**）      |
| B10  | DRAFT + MDFixer         | 环境生成与修复（配对组）    |

## 账号信息

- 秦林炜
- GitHub：[ana12-21](https://github.com/ana12-21)
- 邮箱：221900015@smail.nju.edu.cn / 3353794280@qq.com

## 提交历史（要点）

```bash
git log --oneline | head -20
```

主要 commit：
- `E2: 契约样例 + ADR + Backlog + AI_USAGE`
- `E2: 补齐四类 job 样例 + validate.py + 配对记录`
- `docs: 标注作者账号信息 + 补全文件结构树状图`
- 🆕 `refactor: 把 E2 文件打包到 e2/ 子目录 + 启动 e3/ 骨架`



> 各实验的 ADR / Backlog / AI_USAGE / practice_log 等文档都位于各自子目录的 `docs/` 下，**互不混淆**。

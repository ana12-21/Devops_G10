# DevOps G10 教学实验仓库

> 南京大学苏州校区 2026 秋季 · DevOps 课程 · 10A 组

## 仓库结构



```
DevOps_G10/
├── README.md                       ← 本文件（仓库总览）
│
├── e2/                             ← 实验 2（已完成）
│   ├── README.md                   ← E2 总览
│   ├── contracts/  data/  docs/  scripts/
│
└── e3/                             ← 实验 3（已完成）
    ├── README.md                   ← E3 总览
    ├── fixtures/                   ← A10 样本：MD/RD · C0/C1/C2
    │                                  （DRAFT 由 B10 提供，尚未提交）
    ├── evidence/  scripts/  docs/
    └── work/                       ← 每次运行的原始证据（时间戳目录，只增不改）
```

### 复现方式

```bash
git clone https://github.com/ana12-21/Devops_G10
cd DevOps_G10
python e2/scripts/validate.py --all           # E2 契约校验：应全部 OK
cd e3 && python scripts/run_lab.py            # E3 基线生成：重建 C0/C1/C2 并重跑全部样本
python scripts/render_evidence.py             # 从 work/<ts>/*.json 生成 evidence/*.txt
python scripts/diff_reproducibility.py        # 两次运行的复现性比对：应 OVERALL: PASS
```



## 实验清单

| 实验  | 标题                             | 状态      | 详情                       |
|-------|----------------------------------|-----------|----------------------------|
| **E2** | 需求与接口契约设计               | ✅ 已完成 | [`e2/README.md`](e2/README.md) |
| **E3** | 并行测试基线（MD/RD + C0/C1/C2） | ✅ 已完成 | [`e3/README.md`](e3/README.md) |

## 角色

| 组别 | 服务                   | 职责                       |
|------|------------------------|----------------------------|
| A10  | BuildChecker + EChecker | 依赖检测（**本仓库**）      |
| B10  | DRAFT + MDFixer         | 环境生成与修复（配对组）    |

## 账号信息

- 秦林炜
- GitHub：[ana12-21](https://github.com/ana12-21)
- 邮箱：221900015@smail.nju.edu.cn / 3353794280@qq.com

- 何刘磊
- GitHub：[hll335](https://github.com/hll335)
- 邮箱：241880335@smail.nju.edu.cn

## 贡献分工

| 成员  | GitHub | 提交数 | 主要提交内容（按 git 记录归集） |
|-----|--------|--------|--------------------------------|
| 秦林炜 | [ana12-21](https://github.com/ana12-21) | 16 | E2 契约（`task.schema.json` / `error_codes.md` / `artifact_format.md`）、`validate.py`、E3 样本（md-rd、C0/C1/C2）、`run_lab.py` / `render_evidence.py`、ADR-003 / Backlog / practice_log / AI_USAGE |
| 何刘磊 | [hll335](https://github.com/hll335) | 11 | E2 契约补充（202 创建响应、失败样例、ERROR_REPORT 样例、反例集合）、`versioning.md` / `min_check.md` / `contracts/errors/`、B10 契约对齐（`required` 扩容与枚举约束、`ANALYSIS_5002` 修复器内部异常、REPAIR 候选全败/超时拆分、`sha256` 必需、URI 统一）、README |
| 杨宗乔 | [yangzongqiao](https://github.com/yangzongqiao) | 9 | 补充 A 组 BuildChecker / EChecker 契约包（严格 Schema、OpenAPI、检测样例与校验脚本）；对齐共享 E2 契约中的请求版本与 `trace_id`、响应 `input` 副本、必填 `execution`、CPU 与超时字段，以及 `output.artifacts[]` 产物元数据和 `sha256`。 |

## 提交历史

```bash
git log --oneline | head -20
```

主要 commit：
- `E2: 契约样例 + ADR + Backlog + AI_USAGE`
- `E2: 补齐四类 job 样例 + validate.py + 配对记录`
- `E2(A组): 补齐 202 创建响应、EChecker 失败样例、ANALYSIS_5001、ERROR_REPORT 样例、反例集合、ADR-002`
- `docs: 标注作者账号信息 + 补全文件结构树状图`
- `refactor: 把 E2 文件打包到 e2/ 子目录 + 启动 e3/ 骨架`
- `fix(e3): 重写 README 为真实 E3 任务 + 重构目录为 fixtures/`
- `E3(A组): MD/RD 故障项目 + C0/C1/C2 提交 + run_lab.py 基线生成器 + work 双次跑证据 + Slide 27 对照表`
- `E3(A组): docs/ADR-003 + Backlog + practice_log + AI_USAGE 实质化 + evidence/* 全部就位`
- `E3(A组): 修订 C2 样本（#ifndef 守卫）+ make clean 走真实配方 + 证据路径相对化 + 合成 commit SHA 可复现`



> 各实验的 ADR / Backlog / AI_USAGE / practice_log 等文档都位于各自子目录的 `docs/` 下，**互不混淆**。

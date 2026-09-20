# A 组选定的分析项目（A10 组 · 待补全）

> Backlog T-006 产物：3 个完整 40 位 SHA，可独立 checkout。
> E3 准备阶段需补全；E2 阶段先留占位。

## 选定项目（暂定）

| 字段     | 值（待补全）|
|----------|------------|
| 仓库地址 | `<TODO: GitHub URL>` |
| C0 完整 SHA | `<TODO: 40-char hex>`（BuildChecker 用） |
| C1 完整 SHA | `<TODO: 40-char hex>`（EChecker 增量用） |
| C2 完整 SHA | `<TODO: 40-char hex>`（可选：再向后一个 commit） |

## 选择标准

- C 语言项目（覆盖 BuildChecker/EChecker/MDFixer 适用范围）
- 真实使用 Makefile / Autotools 构建
- 项目有公开 GitHub 仓库、可独立 clone
- commit 历史稳定、对应版本可构建

## E3 时如何消费

```bash
# A 组 BuildChecker
git clone <URL>
git checkout <c0>
# 跑 BuildChecker，输出 actual.json / declared.json / md_report.json

# A 组 EChecker
git checkout <c1>
# 用 c0 的 actual.json 作为 baseline，跑增量检测

# B 组 MDFixer
# 读 c0 的 md_report.json，生成 patch
# 在 c0 commit 上 git apply，验证 build 通过
```

## 候选项目（仅记下与原论文对应的，不一定都用）

| ID     | 项目       | 语言 | 构建系统 | 来源 |
|--------|------------|------|----------|------|
| p-fzy  | fzy        | C    | Makefile | BuildChecker TSE 2024 |
| p-clib | clib       | C    | Makefile | EChecker TOSEM 2024 |
| p-ck   | ck         | C    | Autotools | BuildChecker |
| p-cpython | CPython | C    | Autotools | BuildChecker |
| p-gravity | gravity | C    | Autotools | BuildChecker |
| p-tcpdump | tcpdump | C    | Autotools | BuildChecker |

> 上述 ID 与 SHA 待与 B10 协商后填入。
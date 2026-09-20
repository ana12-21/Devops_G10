# A 组选定的分析项目（A10 组）

> Backlog T-006 产物：**3 个完整 40 位 SHA**。
> E2 阶段先留占位，E3 阶段（T-105）已补全，见下表。

## 选定项目

E3 采用**本仓库内的合成提交**而不是外部开源项目，理由见 `e3/docs/ADR-003.md` 决策 1
（外部项目三步之间掺杂无关 commit，且 HEAD 不稳定，无法保证"唯一变量"）。

| 字段         | 值 |
|--------------|----|
| 仓库地址     | https://github.com/ana12-21/Devops_G10 |
| 样本路径     | `e3/fixtures/commits/{C0,C1,C2}/` |
| C0 完整 SHA  | `7795df52783dac25e6ca08246a2c166431b54ccc`（声明正确，BuildChecker 用） |
| C1 完整 SHA  | `195717d47a4f32ef48aebda8d90055f896b11e21`（新增 include，EChecker 增量用） |
| C2 完整 SHA  | `188ecd7327b805ccb9fe6c2b2a39999b3e892311`（只改编译命令） |
| tag 名       | `C0` / `C1` / `C2` |

## 怎么拿到这三组 SHA 对应的代码

合成 commit 的 `.git/` 目录按设计**不入库**（否则会嵌套仓库、污染主仓库），
所以拿到 SHA 之后需要先本地重建，再 checkout：

```bash
git clone https://github.com/ana12-21/Devops_G10
cd Devops_G10
python e3/scripts/run_lab.py          # 重建 C0/C1/C2 三个带 tag 的仓库

git -C e3/fixtures/commits/C0 rev-parse HEAD   # 应等于 7795df5...（上表 C0）
git -C e3/fixtures/commits/C1 rev-parse HEAD   # 应等于 195717d...（上表 C1）
git -C e3/fixtures/commits/C2 rev-parse HEAD   # 应等于 188ecd7...（上表 C2）
```

**为什么重建后 SHA 一定一样**：`run_lab.py` 给三个合成 commit 固定了作者与提交时间
（`COMMIT_DATES` 常量），SHA 由「内容 + 父提交 + 提交信息 + 时间」唯一决定，
所以任何机器上重跑都会得到同一组哈希。这也是 Slide 5"保存真实 SHA"能做到
"可独立验证"而不是"只有生成它的那台机器认识"的原因。

## E3 时如何消费

```bash
# A 组 BuildChecker：在 C0 上比对 declared vs actual
git -C e3/fixtures/commits/C0 tag             # C0
# 跑 BuildChecker，输出 actual.json / declared.json / md_report.json

# A 组 EChecker：C1 相对 C0 新增 #include "feature.h" → 增量检测
git -C e3/fixtures/commits/C1 tag             # C1
# 用 C0 的 actual.json 作为 baseline

# B 组 MDFixer：读 C0 的 md_report.json 生成 patch，在 C0 上 git apply 验证
```

预期的增量/clean 输出见 `e3/evidence/comparison_table.md`。

## 候选项目（仅记下与原论文对应的，E3 实际未采用）

| ID     | 项目       | 语言 | 构建系统 | 来源 |
|--------|------------|------|----------|------|
| p-fzy  | fzy        | C    | Makefile | BuildChecker TSE 2024 |
| p-clib | clib       | C    | Makefile | EChecker TOSEM 2024 |
| p-ck   | ck         | C    | Autotools | BuildChecker |
| p-cpython | CPython | C    | Autotools | BuildChecker |
| p-gravity | gravity | C    | Autotools | BuildChecker |
| p-tcpdump | tcpdump | C    | Autotools | BuildChecker |

> 上表仅作调研记录。E3 最终选择合成样本，原因：external 项目的三步序列无法保证
> "唯一变量"，且 SHA 会随对方 force-push 失效。

# E3 — 并行测试基线

> 教学实验 E3：为 BuildChecker / EChecker / DRAFT / MDFixer 准备**测试基线样本**

> 本组：**A10**（负责 BuildChecker + EChecker 样本，即 MD/RD 与 C0/C1/C2）


四个工具与各自需要的输入：

| 工具 | 准备输入 | 预期证据 |
|------|----------|----------|
| **BuildChecker** | `main.c` / `Makefile` / 头文件 | **MD、RD 及依据** |
| **EChecker** | `C0/C1/C2` 与历史图预期 | **错误变化与命令变化** |
| **DRAFT**（B10） | README、源码、构建命令 | 成功输出、失败日志 |
| **MDFixer**（B10） | 固定 MD 报告、Makefile | Patch、验证、拒绝案例 |

E3 实验包里 A 组只负责 BuildChecker + EChecker 两条线——MD/RD 与 C0/C1/C2。

---

## 一、MD / RD 样本（BuildChecker 输入）

| 文档 | 全称 | 触发场景 | 关键字段 |
|------|------|----------|----------|
| **MD** | Missing Dependency | Makefile 中**未声明**某个被源文件读取的头文件 | 触发条件 + 人工依据 + 修复 patch |
| **RD** | Redundant Declaration | Makefile 中**声明了**某个未被源文件读取的头文件 | 触发条件 + 多余编译输出 + 修复 patch |

**示例样本**（`fixtures/md-rd/`）：

```c
// main.c
#include <stdio.h>
#include "config.h"   // ← 真实被读取
int main(void) {
    printf("%d\n", VALUE);
    return 0;
}

// config.h
#define VALUE 1

// unused.h
/* still unused */  // ← 真实未被读取
```

```makefile
# Makefile（MISSING config.h + REDUNDANT unused.h）
main.o: main.c unused.h
    cc -c main.c -o main.o

app: main.o
    cc main.o -o app
```

**人工答案**（`fixtures/md-rd/oracle.json`）：

```json
{
  "provenance": "INSTRUCTOR_ORACLE",
  "findings": [
    {"type": "MISSING",   "target": "main.o", "dependency": "config.h"},
    {"type": "REDUNDANT", "target": "main.o", "dependency": "unused.h"}
  ]
}
```

**预期观察**（PPT slide 18-21）：

| 操作 | 预期输出 | 解释 |
|------|----------|------|
| `make && ./app`（首次） | `1` | config.h = VALUE 1，构建并执行 |
| 改 `config.h` 为 `VALUE 2`，再 `make && ./app` | **仍 `1`** | Makefile 缺 `config.h` 依赖，漏重建 |
| `make clean && make && ./app` | `2` | 同一源码全量重建 |
| 改 `unused.h` 注释，再 `make` | 触发 `cc -c main.c -o main.o` | 出现多余编译 |

---

## 二、C0 / C1 / C2 真实提交（EChecker 输入）

三个 Git tag 模拟**项目从正确到引入缺陷**的真实演化：

| 版本 | 改动 | 工具预期 | clean build 输出 |
|------|------|----------|------------------|
| **C0** | 声明正确：`main.o: main.c config.h` | 无 MD/RD | `10`（`BASE=10`, `MODE=0`） |
| **C1** | 新增 `#include "feature.h"`，**Makefile 未声明** | **MD: main.o 缺 feature.h** | `12`（`+ FEATURE=2`） |
| **C2** | **只改编译命令** `CFLAGS = -O0 -DMODE=7` | 命令变化应触发重编译但未触发普通重建 | 增量 = `12`，clean = `19` |

**示例源码（C0）**：

```c
// main.c
#include <stdio.h>
#include "config.h"
int main(void) {
    printf("BASE=%d FEATURE=%d MODE=%d\n", BASE, FEATURE, MODE);
    return 0;
}

// config.h
#define BASE 10

#ifndef MODE          // C0/C1/C2 统一用这个写法：C2 靠 -DMODE=7 覆盖默认值，
#define MODE  0       // 裸 #define 会盖掉命令行宏，样本就退化了（见 ADR-003 决策 3）
#endif

// C1 才会出现
// feature.h
// #define FEATURE 2
```

```makefile
# Makefile（C0）
main.o: main.c config.h
    cc -c main.c -o main.o

# C1 改 main.c 加 #include "feature.h"
# C1 Makefile 保持不变（不声明 feature.h）

# C2 Makefile 仍保持不变
# C2 CFLAGS: -O0 → -O0 -DMODE=7
```

---

## 三、DRAFT 样本（B10 负责，**本仓库尚未收到**）

---

## 四、目录结构

```text
e3/
├── README.md                          ← 本文件（E3 总览）
│
├── fixtures/                          ← 🆕 测试样本
│   │
│   ├── md-rd/                         ← MD/RD 样本项目（A10 主线）
│   │   ├── main.c
│   │   ├── config.h
│   │   ├── unused.h
│   │   ├── Makefile
│   │   └── oracle.json                ← 人工答案（INSTRUCTOR_ORACLE）
│   │
│   ├── commits/                       ← C0/C1/C2 真实提交（A10 主线）
│   │   ├── C0/                        ← 声明正确
│   │   │   ├── main.c
│   │   │   ├── config.h
│   │   │   ├── Makefile
│   │   │   └── .git_info.txt          ← tag = C0, sha = <真实>
│   │   ├── C1/                        ← 新增 include（MD）
│   │   │   ├── main.c
│   │   │   ├── config.h
│   │   │   ├── feature.h
│   │   │   ├── Makefile
│   │   │   └── .git_info.txt
│   │   └── C2/                        ← 只改编译命令
│   │       ├── main.c
│   │       ├── config.h
│   │       ├── feature.h
│   │       ├── Makefile
│   │       └── .git_info.txt
│   │
│   └── draft/                         ← DRAFT 样本（B10 负责；目前只有 .gitkeep）
│
├── evidence/                          ← 命令日志（由 scripts/render_evidence.py 从 work/ 生成）
│   ├── env_check.txt                  ← 环境版本（OS / CPU / git / make / gcc / python / recipe shell）
│   ├── build_md-rd.txt                ← md-rd 三步：MD 漏重建 → clean 生效 → RD 多余编译
│   ├── build_c0.txt                   ← C0 clean 构建日志
│   ├── build_c1.txt                   ← C1 clean 构建日志
│   ├── build_c2.txt                   ← C2 真实迁移：增量 12 → clean 19
│   └── comparison_table.md            ← 增量 vs clean 对照表
│
├── scripts/                           ← 跑数据 / 验证脚本
│   ├── run_lab.py                     ← 主入口（PPT slide 17 提及）
│   ├── render_evidence.py             ← 从 work/<ts>/*.json 生成 evidence/*.txt
│   └── diff_reproducibility.py        ← 两次运行的复现性比对
│
├── work/                              ← 每次运行的原始证据（时间戳目录，只增不改）
│   ├── <YYYYMMDD-HHMMSS>/*.json       ← 命令序列 + 观察结论（机读）
│   ├── reproducibility_rerun.log      ← 第二次运行的完整输出
│   └── reproducibility_diff.log       ← 两次运行剔除 ts 后的比对结果
│
└── docs/                              ← E3 自己的文档
    ├── ADR-003.md                     # C0/C1/C2 设计决策
    ├── Backlog.md                     # T-101~T-116 E3 任务表
    ├── AI_USAGE.md                    # AI 使用记录（E3 部分）
    └── practice_log.md                # E3 实践日志
```

---

## 五、实验流程（Backlog 摘要）

| 阶段 | 任务 | 产物 |
|------|------|------|
| **T-101** | 选定 1 个 MD 样本项目（GNU Make + C），写 `fixtures/md-rd/` | 完整可跑的小项目 |
| **T-102** | 写人工答案 `fixtures/md-rd/oracle.json` | INSTRUCTOR_ORACLE 标记 |
| **T-103** | 验证 MD 现象：改头文件不重建，clean build 才生效 | `evidence/build_md-rd.txt` |
| **T-104** | 验证 RD 现象：改 unused 头文件触发多余 cc | `evidence/build_md-rd.txt` |
| **T-105** | git tag C0（声明正确）→ git tag C1（新增 include）→ git tag C2（只改命令） | `fixtures/commits/C0,C1,C2/.git_info.txt` |
| **T-106** | 在每个 commit 上跑增量 + clean build，记录预期输出 | `evidence/build_c0.txt`、`build_c1.txt`、`build_c2.txt` |
| **T-107** | 写对照表 `evidence/comparison_table.md`（C0/C1/C2 增量 vs clean） | 对照表 |
| **T-108** | 在 Linux 环境跑 strace，记录 `config.h` 访问 | `evidence/linux-verified/`（➖ 本机无容器） |
| **T-109** | 撰写 ADR-003（C0/C1/C2 设计决策） | `docs/ADR-003.md` |
| **T-110** | 撰写 AI_USAGE（E3 部分）+ 补充 Backlog + practice_log | `docs/*.md` |
| **T-113~T-116** | 复核后补齐：环境证据、证据生成脚本、SHA 可复现、路径相对化 | `evidence/env_check.txt`、`scripts/render_evidence.py` |




### A10 组

- [x] `fixtures/md-rd/` 项目完整（main.c / config.h / unused.h / Makefile / oracle.json）
- [x] oracle.json 含 2 条 finding（1 MISSING + 1 REDUNDANT），`provenance = INSTRUCTOR_ORACLE`
- [x] `evidence/build_md-rd.txt` 证明改 config.h 后 `make` 输出旧值、clean build 后输出新值
- [x] `evidence/build_md-rd.txt` 证明改 unused.h 触发 `gcc -c main.c -o main.o`
- [x] `fixtures/commits/C0/C1/C2/` 各含 `.git_info.txt`（真实 tag + SHA，且 SHA 可复现）
- [x] C0/C1/C2 三个 commit 在 `evidence/build_c{0,1,2}.txt` 中记录增量 vs clean 输出
- [x] `evidence/comparison_table.md` 对照表完整（C2 增量 12 / clean 19，与 PPT 一致）
- [x] `evidence/env_check.txt` 记录 OS / CPU / 工具链版本
- [x] `work/` 存两次运行证据，`work/reproducibility_diff.log` = `OVERALL: PASS`
- [x] `docs/ADR-003.md`、`docs/Backlog.md`、`docs/AI_USAGE.md`、`docs/practice_log.md` 四份齐全
- [ ] `evidence/linux-verified/` 含 strace 记录 —— 本机无 Linux 容器，列为可选（T-108）
- [ ] `fixtures/draft/` DRAFT 样本 —— 由 B10 提供，尚未提交

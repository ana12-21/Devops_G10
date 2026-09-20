# E3 — 并行测试基线

> 教学实验 E3：为 BuildChecker / EChecker / DRAFT / MDFixer 准备**测试基线样本**
> 教师：吕骏 ｜ 助教：曾星伟
> 日期：2026-09-20 起
> 本组：**A10**（负责 BuildChecker + EChecker 样本，即 MD/RD 与 C0/C1/C2）

---

## ⚠️ E3 的真实定位（纠正此前误判）

E3 **不是**"分析 6 个外部开源项目"——E3 的真实任务是：

> **为四个工具准备测试样本，使它们能跑、能判断对错、能互相比较**

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

## 三、DRAFT 样本（B10 准备的参考样本）

DRAFT 项目（`fixtures/draft/`）：

```c
// main.c
#include <stdio.h>
int main(void) {
    printf("hello E3\n");
    return 0;
}
```

```makefile
# Makefile
all:
    cc -o hello main.c

clean:
    rm -f hello
```

两层成功判据：

| 层级 | 检查 | 预期 |
|------|------|------|
| **第一层：编译通过** | `make` 退出码为 0 | `hello` 可执行文件生成 |
| **第二层：功能验证** | `./hello` 退出码为 0 | 输出 `hello E3` |

失败候选（B10 提供）：`Dockerfile.broken`（无 `gcc`/`make`）→ 非零退出码。

---

## 四、目录结构（修正后）

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
│   └── draft/                         ← DRAFT 样本（B10 准备，A10 参考）
│       ├── main.c
│       ├── Makefile
│       └── README.md
│
├── evidence/                          ← 命令日志
│   ├── env_check.txt                  ← 环境版本（git/make/cc/python3 + strace）
│   ├── build_c0.txt                   ← C0 增量 + clean 构建日志
│   ├── build_md_unbuilt.txt           ← MD 漏重建日志（仍输出旧值）
│   ├── build_md_clean.txt             ← MD clean build 日志（输出新值）
│   ├── build_rd_unused.txt            ← RD 多余编译日志
│   ├── build_c1.txt                   ← C1 增量 + clean 构建日志
│   ├── build_c2.txt                   ← C2 增量 + clean 构建日志
│   └── comparison_table.md            ← 增量 vs clean 对照表
│
├── scripts/                           ← 跑数据 / 验证脚本
│   ├── run_lab.py                     ← 主入口（PPT slide 17 提及）
│   └── verify_docker.py               ← Docker 验证（PPT slide 12 提及）
│
└── docs/                              ← E3 自己的文档
    ├── ADR-003.md                     # C0/C1/C2 设计决策（待）
    ├── Backlog.md                     # T-101~T-110 E3 任务表（待）
    ├── AI_USAGE.md                    # AI 使用记录（E3 部分）
    └── practice_log.md                # E3 实践日志（待）
```

> 📌 **修正点**：原来 `md_samples/` 和 `commits/` 改为 `fixtures/{md-rd,commits,draft}/`——符合 PPT slide 12 建议的"fixtures 目录结构"。

---

## 五、实验流程（Backlog 摘要）

| 阶段 | 任务 | 产物 |
|------|------|------|
| **T-101** | 选定 1 个 MD 样本项目（GNU Make + C），写 `fixtures/md-rd/` | 完整可跑的小项目 |
| **T-102** | 写人工答案 `fixtures/md-rd/oracle.json` | INSTRUCTOR_ORACLE 标记 |
| **T-103** | 验证 MD 现象：改头文件不重建，clean build 才生效 | `evidence/build_md_*.txt` |
| **T-104** | 验证 RD 现象：改 unused 头文件触发多余 cc | `evidence/build_rd_*.txt` |
| **T-105** | git tag C0（声明正确）→ git tag C1（新增 include）→ git tag C2（只改命令） | `fixtures/commits/C0,C1,C2/.git_info.txt` |
| **T-106** | 在每个 commit 上跑增量 + clean build，记录预期输出 | `evidence/build_c0.txt`、`build_c1.txt`、`build_c2.txt` |
| **T-107** | 写对照表 `evidence/comparison_table.md`（C0/C1/C2 增量 vs clean） | 对照表 |
| **T-108** | 在 Linux 环境跑 strace，记录 `config.h` 访问 | `evidence/linux-verified/` |
| **T-109** | 撰写 ADR-003（C0/C1/C2 设计决策） | `docs/ADR-003.md` |
| **T-110** | 撰写 AI_USAGE（E3 部分）+ 补充 Backlog + practice_log | `docs/*.md` |

---

## 六、提交要求（PPT slide 9/10）

### A 组

| 必交 | 内容 |
|------|------|
| **MD/RD 项目和判断依据** | `fixtures/md-rd/` + `evidence/build_md_*.txt` + `evidence/build_rd_*.txt` |
| **C0/C1/C2 版本及预期变化** | `fixtures/commits/{C0,C1,C2}/` + `evidence/build_c{0,1,2}.txt` |

### 共同信息

| 必交 | 内容 |
|------|------|
| README、环境、命令与日志 | `README.md` + `evidence/env_check.txt` |
| 仓库、SHA 与个人贡献 | `fixtures/commits/*/.git_info.txt` |
| 当前代码与失败日志 | `fixtures/` 源码 + `evidence/` 日志 |
| 卡在哪里、试过什么、下一步 | `docs/practice_log.md` |

> ⚠️ **未完成也要记录**——遇到任何阻塞直接写在 `docs/practice_log.md`，不要等。

---

## 七、验收清单（E3）

### A10 组

- [ ] `fixtures/md-rd/` 项目完整（main.c / config.h / unused.h / Makefile / oracle.json）
- [ ] oracle.json 含 2 条 finding（1 MISSING + 1 REDUNDANT），`provenance = INSTRUCTOR_ORACLE`
- [ ] `evidence/build_md_unbuilt.txt` 证明改 config.h 后 `make` 输出旧值
- [ ] `evidence/build_md_clean.txt` 证明 clean build 后输出新值
- [ ] `evidence/build_rd_unused.txt` 证明改 unused.h 触发 cc -c
- [ ] `fixtures/commits/C0/C1/C2/` 各含 `.git_info.txt`（真实 tag + SHA）
- [ ] C0/C1/C2 三个 commit 在 `evidence/build_c{0,1,2}.txt` 中记录增量 vs clean 输出
- [ ] `evidence/comparison_table.md` 对照表完整
- [ ] `evidence/linux-verified/` 含 strace 记录（如果环境允许）
- [ ] `docs/ADR-003.md`、`docs/Backlog.md`、`docs/AI_USAGE.md`、`docs/practice_log.md` 四份齐全

### 评审标准（PPT slide 10 相互检查）

- [ ] 别人能按 README 重跑项目
- [ ] 人工答案和实际日志分得清
- [ ] 预期结果能说明依据
- [ ] 失败记录能定位到具体 commit

---

## 八、后续安排（PPT slide 10）

| 实验 | 主题 |
|------|------|
| **E4** | 环境和密钥管理 |
| **E5** | BuildChecker / DRAFT 实现 |
| **E8** | EChecker / MDFixer 实现 |
| **E12** | 接入真实数据联调（A 组 B 组打通） |

---

## 九、与 E2 的关系

- **E2 是契约设计**：契约格式、错误码、URI 体系。
- **E3 是测试样本**：MD/RD 报告格式参考 E2 的契约字段（`provenance`、`findings`）。
- **E2 已产出的两份 ADR（E3 必须对齐）**：
  - `e2/docs/ADR-001.md` — 异步 Job 模式（四类任务的统一模型，E3 四条线都建在它之上）
  - `e2/docs/ADR-002.md` — **系统执行错误与检测发现分离**：检测出 `MISSING` / `REDUNDANT` 时
    任务状态仍为 `SUCCEEDED`，只有平台或工具自身故障（`ENV_3002` / `EXEC_4002` / `ANALYSIS_5001`）
    才写 `job.error`。**E3 的 EChecker 预期变化直接由它决定**——"发现数 > 0" ≠ 任务失败。
- **ADR 编号接续**：E2 已占用 ADR-001 / ADR-002，故 E3 首份 ADR 从 **ADR-003** 起编号。
- E3 完成后，E4-E12 会在此基础上构建完整工具链——E2 的契约会被 EChecker / MDFixer 直接消费。
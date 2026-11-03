# 决策记录（E8 A 轨道）

## 背景与约束

E8 要求在**不重复执行完整构建**的前提下，判断本次提交相对历史基线是否需要重新做依赖分析。样例是一个受限的 C/Make 项目：两个对象目标 `main.o`、`helper.o`，`CFLAGS` 只允许 `-O0`/`-O1`/`-O0 -DMODE=1`，Makefile 只支持显式规则加简单变量替换。

约束来自三处：

1. 参考实现 `labs/e8e10/lab.py` 已把支持范围显式收窄，超出范围抛 `UNSUPPORTED_DECLARATION` / `UNSUPPORTED_FLAGS`，不允许猜测。
2. 基线必须可追溯到真实构建，不能只用 `gcc -MM` 这类静态近似充当历史图。
3. 个人贡献只能落在 `labs/e8e10/test_profile.py`，不得改动被测实现。

## 选择与替代方案

### A：缓存何时失效、配置身份如何绑定

**选择**：把「全部本地 `.c/.h` 的预处理指令行 + Makefile 中 TAB 开头的配方行 + `CFLAGS` + 编译器版本首行」组合成一个 `key`，作为唯一缓存身份。`key` 相等才允许复用 `actual`/`findings`，否则所有目标统一 refresh。

**替代方案 1：按文件修改时间（mtime）判断**。实现最省事，但 mtime 会被 `git checkout`、`cp -p`、容器挂载无意义地刷新，且无法区分「注释改了」和「#include 改了」，误判率高。否决。

**替代方案 2：按 git commit 是否相同判断**。太粗：同一 commit 内的工作区改动会被当作未变化（假复用），而不同 commit 仅改注释会被当作全量失效（假刷新）。否决。

**替代方案 3：per-target 精细失效（只 refresh 依赖闭包含变更头文件的目标）**。更贴近理想，但要为每个目标单独维护头文件闭包，且闭包本身依赖于上一次分析结果，一旦上次结果错就会持续错。当前样例只有两个目标，收益为零，风险却真实存在。暂缓，写进扩展计划。

**选择理由**：`key` 的四个成分恰好覆盖了会改变预处理结果的所有输入维度。预处理指令行而不是整文件内容，是因为注释和空行变化不影响编译产物，用指令行可以减少不必要的失效。

### B：配置身份绑定——为什么把编译器版本放进 `key`

同一份源码用不同 gcc 版本可能展开出不同的系统头文件依赖。把 `gcc --version` 首行纳入 `key`，可以让「换编译器」这件事自动触发全量重算，而不需要在别处硬编码版本判断。代价是镜像重建后（即使 gcc 版本字符串没变但构建号变了）也会失效一次，可接受。

### 关于历史图来源

**选择**：`baseline.json` 的 `actual` 最终取自真实 BuildChecker 的 `actual-graph.json`（`strace -ff` + `make -p` 的产物），而不是 `gcc -MM` 的输出。

**理由**：论文的核心论点是「从真实执行中学习依赖」，如果基线用静态工具生成，就绕开了要被验证的机制。`gcc -MM` 的角色降级为**交叉核对**：`buildchecker()` 内部断言真实图投影与 `gcc -MM` 在对象目标上完全一致，两者不一致就直接失败，避免「真实图错了但没人发现」。`baseline_source` 字段把这个来源显式写进产物，报告和审计都能看出来。

**替代方案**：只用 `gcc -MM` 建图。更快且不依赖 `SYS_PTRACE`，但无法证明真实执行被观测过。否决。

## 代价与覆盖范围

|维度|当前能力|明确不支持|
|---|---|---|
|目标数|任意个 `.o`，逐目标比对|模式规则（`%`）、静态模式规则|
|依赖采集|`gcc -MM`，受限 `CFLAGS`|`-D` 宏变化以外的编译选项、条件编译分支|
|失效粒度|全局（一个 `.h` 变化→全部 refresh）|按目标精细失效|
|Makefile|显式规则 + 简单变量展开（最多 8 层）|`$(shell ...)`、`include`、order-only 依赖参与判定|
|复用安全|`key` 覆盖预处理指令与配方|跨编译器内部头文件差异的等价性|

代价的实质是**过度刷新**（性能损失）换取**不漏刷新**（正确性）。对本样例两个目标、分析耗时在 30 ms 量级的情况下，这个取舍是正确的；目标数上千时就该往精细失效走。

## 验证命令与实际证据

个人新增测试 `StudentE8A::test_indirect_include_in_header_invalidates_old_graph` 直接验证了「配置身份绑定」这一决策：在 `config.h` 内新增 `#include "extra.h"`（`main.c` 一字未改）后，断言 `reused==[]`、两个目标都 refresh、`main.o` 的真实依赖变成三个文件、并产生 `MISSING main.o → extra.h`。

变异检验证明这个决策不是空话：把 `key` 中的 `directives` 字段删掉（退化为只看配方），测试立刻报 `AssertionError: 'extra.h' not found in ['config.h', 'main.c']`。说明该字段是「头文件内容变化必须触发失效」这一行为的唯一保证。

完整证据见 `$OUT/`（`work/e8-A-manual.MA9l1R`）：`baseline.json`、`incremental.json`、`buildchecker/{actual-graph.json,declared-graph.json,make-db.txt,trace/,findings.json}`、`steps/` 下每一步的容器日志与 `STEP_EXIT_CODE`。

## E9 追加决策：实际图与声明图分开维护

**选择**：`scan()` 把 `actual`（真实读取，来自 `gcc -MM` 或历史图）与 `declared`（Makefile 解析结果）作为两套独立数据，`findings` 每次都由二者现算，`key` 只覆盖 `actual` 的失效条件。

**替代方案：把 `findings` 一起缓存**。看上去更省，但 C3 场景直接反证：只改声明行时 `actual` 完全可复用，而 `findings` 必须重算——否则 C3 会继续报告两条已被修复的 MD。E9 的 `C3_RESOLVED_PASS` 就是这个错误做法的反例。

**代价**：每次 `scan` 都要重新解析 Makefile（文本解析，微秒级）。这与 `gcc -MM` 子进程（毫秒级）相比可以忽略，所以这个代价实际上是负的——用极小的解析开销换来了声明变更的即时生效。

**验证**：`StudentE9A` 断言 `c3['key']==c2['key']`、`reused` 为两目标、`resolved` 恰为两条 MD、RD 保留。把复用分支的 `resolved` 强制置空后测试失败。

## E10 追加决策：计时口径与离群值处理

**选择**：计时直接用 `time.perf_counter()` 包住 `scan()`，包含 Git 调用、编译器版本探测、Makefile 解析、`gcc -MM` 子进程；**不包含** clean build。每类跑 5 次取中位数，离群值不剔除。

**理由**：目的是比较「同一分析任务的两条路径」，所以只应计入 `scan` 自身。如果计入 clean build，两种路径的构建开销相同，会稀释掉真正的差异。用中位数而不是平均值，是因为 `unchanged`/`declaration` 的第 1 次都有明显冷启动（0.0091 s / 0.0055 s，其余 4 次 0.0017 s），平均值会被单个离群值拉偏。

**不剔除离群值的理由**：5 个样本剔除 1 个就只剩 4 个，中位数会变成两点平均，反而更不稳定；而且冷启动是真实存在的成本，应当记录。原始值全部留在 `results.csv`，读者可以自行判断。

**结果解读必须诚实**：`unchanged`/`body`/`declaration` 的 5.8 倍加速来自跳过两次 `gcc -MM`；`include`/`flags`/`header` 的 ≈1.0 则说明刷新路径没有收益。不能只报 5.8 倍而隐去 1.0——后者才是这个粗粒度 key 的真实代价。

## E10 追加决策：为什么比较完整三元组而不是发现条数

**选择**：`passed=all(inc[k]==full[k] for k in ['actual','declared','findings'])`，逐项比完整集合。

**替代方案：只比较 `len(findings)`**。会放过一类严重错误——把 `MD main.o→config.h` 误报成 `MD main.o→extra.h`，条数同样是 1，但结论完全不同。E10 的 `include` 场景里 MD 从 config.h 变成 config.h + extra.h，如果只比条数，C3 之后「MD 全部消除」与「MD 换了个依赖」也无法区分。

**代价**：需要保存完整的 `actual`/`declared`/`findings` 快照（每场景 5 对 JSON）。存储开销可以忽略，换来的是可复核性——每份 JSON 都能单独打开核对。

# 决策记录

## 背景与约束

A 组 E8—E10 要求在不改动 BuildChecker 的前提下，为对象级依赖检查加一层历史图复用。约束有四条：

1. 依赖图的唯一真实来源是 BuildChecker 在 strace 下采出的 `actual-graph.json`，不能只靠 `gcc -MM` 猜。
2. 被测样例只支持受限配置：显式 Makefile、`main.o`/`helper.o` 两个对象目标、gcc 本地头文件，`-I`/`-D` 之外的复杂配置不在支持范围。
3. 增量结果必须与全量结果一致，任何“更快但更不准”的优化都不成立。
4. 容器运行时无网络，所有产物只能落在 `work/<OUT>` 内，不能污染被测工程。

## 选择与替代方案

**A：缓存何时失效、配置身份如何绑定**

- 选择：用一个全局失效键 `key`，内容为“全部 `.c/.h` 的预处理指令（`#include`/`#define`）+ Makefile 配方行 + `CFLAGS` + `gcc --version`”。键相等则两个目标都复用旧图；键不等则两个目标都重建。
- 替代方案一：按目标做局部指纹（本目标的源文件 + 当前已知依赖 + 配方）。它能把 header 变更的刷新面缩小到真正包含它的目标。
- 替代方案二：只比较文件 mtime/size。实现最省事，但 `git checkout`、重新 clone 后全部失配，且无法覆盖 Makefile 配方变化。
- 选择理由：C2 场景里 `main.c` 新增 `#include "extra.h"`，而这个头文件在旧图中根本不存在，局部指纹无法在扫描前判断“哪个目标会被新头文件影响”，只有全局指令集能保证不漏检。mtime 方案与 E10 的 unchanged 场景直接冲突（重新提交后时间戳变化但内容不变，应复用）。

**B：共享变量怎样处理、失败怎样保证原目录不变**

- 选择：`scan()` 复用 `old['actual']`（真实图），从不复用 `old['findings']`；`findings` 每次都按当前 Makefile 的 `declared` 重新计算，`added/resolved` 是新旧 `findings` 的差集。
- 替代方案：把整份结果（含 findings）当缓存直接返回。C3 会立刻暴露问题——C3 只改 Makefile 声明，图可以复用，但两条 MISSING 必须变成 resolved，缓存结论会让检查失效。
- 失败边界：`scan()` 只读工程目录，所有输出写到 `OUT`；重建失败时旧 `old` 对象不被修改，下一次仍可基于上一份成功结果重试。

**C：环境镜像的构建源**

- 选择：`labs/e8e10/environment/services/buildchecker/Dockerfile` 原样保留在仓库中，但本机构建时清华镜像返回 HTTP 403（`mirrors.tuna.tsinghua.edu.cn` 的 Debian 源与 PyPI 均不可用），因此在 `/tmp/e8env` 的临时副本里把镜像站替换为阿里云后构建，再打上 `course-e8e10:221900015` 标签。
- 代价：镜像 ID 与在能访问清华源的机器上构建的结果不同，但基础镜像、包集合、gcc/make/python 版本一致（gcc 14.2.0、make 4.4.1、pytest 8.4.2）。仓库内 Dockerfile 未被修改，CI 在 GitHub 上仍按原文件构建。
- 替代方案：`docker build --cache-from course-e8e10:241880335` 复用同学镜像层，实测旧版构建器未命中缓存，仍会走网络，故放弃。

## 代价与覆盖范围

- header/include/flags 三类变化下没有加速：增量中位数与全量之比分别为 1.00、0.99、0.98。这是保守失效的直接代价。
- 复用场景也只快约 5.7—5.9 倍而不是数量级，因为耗时里包含容器内 Python 启动、git 调用和 JSON 解析的固定开销（约 1.7 ms 下限）。
- 覆盖不到：并行 `make -j` 的进程归并、隐式规则、生成的源文件、系统头文件变化。被测样例不涉及这些路径，CI 的受限配置检查会对越界输入显式拒绝。

## 验证命令与实际证据

```bash
# 1. 单测：原包 7 项 + 本人 2 项
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$PWD:/course" -w /course course-e8e10:221900015 \
  python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v
# -> Ran 9 tests ... OK

# 2. E10 矩阵一致性
cat work/e10-A-manual.1kYmmv/matrix/gate.json
# -> {"track":"A","passed":true,"rows":30}

# 3. 复用判定
cat work/e8-A-manual.GfMg98/incremental.json
# -> "reused":["main.o","helper.o"], "refreshed":[], "added":[]
```

证据文件：`work/e8-A-manual.GfMg98/`、`work/e9-A-manual.cviTAV/`、`work/e10-A-manual.1kYmmv/`、`work/unit-tests-*.log`、`work/environment-build-*.log`。

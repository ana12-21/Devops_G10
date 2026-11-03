# AI使用记录

## 工具/模型/日期

- 工具：GitHub Copilot（VS Code Chat，Agent 模式）
- 模型：deepseek-flash
- 日期：2026-11-03

## 输入上下文与问题

本轮与模型交互的范围限定为**执行与排错**，不含算法设计：

1. 按 `02_操作手册/00_公共准备.md` 在云主机上完成从登录到可开始 E8 的全部准备步骤。
2. 按 `8_E8_A组.md` 逐步执行 E8 A 轨道的第 0–7 步。
3. 完成第 8 步要求的自主扩展测试，并证明它能捕获回归。

提供给模型的上下文：分发包 `DevOps_E8_E10_20261031` 的操作手册与 `03_实验包` 源码、云主机 SSH 凭据（密钥路径）、本组仓库地址。

## 模型建议

**环境准备阶段**（4 项，均为操作性问题）：

| 问题 | 模型建议 | 是否采纳 |
|---|---|---|
| `gh` 未安装，apt 只有 2.4.0 | 从 `ghfast.top` 镜像下载 2.103.3 官方二进制装到 `/usr/local/bin` | 采纳，已生效（`gh version 2.103.3`）|
| `Compress-Archive` 打包后中文目录名乱码 | 改用 Python `zipfile` 写正斜杠与 UTF-8 标志，解压也用 `zipfile.extractall` | 采纳，316 个文件路径全部正常 |
| `gh auth login` 非 TTY 下不输出验证码，`script` 伪终端无法回应 ANSI 查询 | 用 `tmux` 会话 + `send-keys`/`capture-pane` 完成设备码流程 | 采纳 |
| Dockerfile 里 tuna 镜像返回 403 | 先测多个镜像，确认 nju/aliyun/ustc/huaweicloud 可用；**临时**替换后构建，完成后 `git checkout` 还原 | 采纳，但还原校验由我亲自确认（blob 哈希 `bcf3a7be` 前后一致）|

**E8 实验阶段**：模型只负责把手册里的命令转成可执行的 bash 脚本并上传，没有提出任何关于 MD/RD 判定、缓存失效策略的改动建议。

**自主测试阶段**：模型给出的测试思路是「在 `config.h` 里加间接 include」，我核对后采纳；**四条独立预期是我自己先推导再写进断言的**（见下）。

## 采纳/拒绝及理由

**采纳**：上述 4 项环境处置。理由是它们只影响"能不能跑起来"，不影响实验结论。

**拒绝 1：模型曾建议直接修改仓库里的 Dockerfile 把 tuna 换成 nju 并合入 main。** 拒绝理由：这会让学生代码与分发包 `03_实验包` 的 Dockerfile 不再逐字节一致，验收时无法用「与教学参考相同」来证明未篡改。改为临时替换 + 构建后还原。

**拒绝 2：模型曾建议用 `workflow_dispatch fail_demo=true` 的参数注入来演示 CI 失败。** 该建议属于 E7 阶段遗留讨论，本次不涉及；记录在此仅为说明——参数注入产生的失败不能等同于「真实提交被门禁拦下」，这类"看起来通过但语义不同"的做法一律不采用。

**未采用模型的任何算法层建议**：`lab.py` 的 `key` 构成、失效粒度、`gcc -MM` 与真实图的交叉核对关系，全部来自参考实现与手册，模型未参与设计。

## 人工修改

1. **测试断言全部由我独立推导后填写**。写测试前先在纸上/终端里推演：`config.h` 加 `#include "extra.h"` 后，`main.o` 的真实依赖应是 `config.h`/`extra.h`/`main.c`；`helper.o` 的翻译单元未变但 `key` 变了所以也要 refresh；新增发现应为 `MISSING main.o → extra.h`。四条预期先写成注释，再转成 `assertEqual`/`assertIn`。没有把代码跑出来的值直接抄成预期。
2. **测试类名与文档风格对齐**：按 `08_个人测试编写示例.md` 要求使用 `StudentE8A`，并在类文档字符串里写明「学生补充（241880335）」。
3. **变异检验由我设计并执行**：模型未建议这一步。我在 `/tmp` 副本里删掉 `key` 的 `directives` 字段，确认同一测试报 `AssertionError: 'extra.h' not found in ['config.h', 'main.c']`，用来证明测试不是"恒真断言"。变异副本用完即删，原仓库 `lab.py` 未动。
4. **报告与 ADR 中的数字全部来自实际输出**：`trace_id=e6-65b9f4405e034a9abd3f0dc9184e2380`、`make-db.txt` 第 1044 行、`t.15:579` / `t.16:23`、内层 C0 `88feb8a`、镜像 `sha256:878c2e21…`，均逐条对照 `$OUT` 下的文件核对，没有沿用教师示例的行号。

## 实际验证命令/输入/结果

|目的|命令|结果|
|---|---|---|
|全量测试|`docker run … python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`|`Ran 8 tests … OK`，`TEST_EXIT=0`（原 7 项 + 新增 1 项）|
|新增测试单独跑|`PYTHONPATH=/course/labs/e8e10:/app … -m unittest test_profile.StudentE8A -v`|`ok`，`Ran 1 test`|
|变异后同一测试|`key` 删 `directives` 后跑同一测试|`FAILED (failures=1)`，`'extra.h' not found in ['config.h', 'main.c']`|
|一键门禁|`python3 run_lab.py e8 --track A --out work/e8-A-verify-094309`|`COMPLETED e8 A`，`GATE_EXIT=0`|
|Dockerfile 还原|`git hash-object` 前后比对|`bcf3a7be7bce…` 前后一致，`git status` 干净|

## 参考实现与本人贡献边界

**来自参考实现（未改动）**：`labs/e8e10/lab.py` 全部函数（`fixture`/`scan`/`patch`/`validate`/`buildchecker`/`demo`）、`test_profile.py` 原有 `ProfileTests` 的 7 项测试、`environment/` 下的 BuildChecker 与 Dockerfile。

**本人贡献**：仅 `labs/e8e10/test_profile.py` 中新增的 `StudentE8A` 类（23 行，1 个测试方法）。其余动作是执行手册命令、采集证据、填写报告。

**环境处置（未进版本库）**：`gh` 二进制安装、`GH_CONFIG_DIR` 认证目录、Docker `registry-mirrors`、构建时的镜像源临时替换。这些都属于课堂环境适配，不构成对实验代码的贡献，已在报告「未完成项」中如实说明。

## E9 / E10 追加记录（同日）

**输入上下文与问题**：按 `9_E9_A组.md` 与 `10_E10_A组.md` 执行 E9 的第 0–10 步和 E10 的第 0–13 步，然后各完成一次自主扩展测试。

**模型建议**：本阶段模型只做两件事——把手册命令转成可执行 bash 脚本、把输出汇总成表格。**没有对 `lab.py` 的实现、缓存策略、失效粒度提出任何修改建议**，也没有建议改动手册给出的断言。

**逐项说明**：

|项|模型是否参与|说明|
|---|---|---|
|E9 四个提交的内容与顺序|否|完全按手册第 4/6/8 步|
|E9 `C1/C2/C3` 断言|否|手册原文，未改动|
|E10 六场景 × 5 次|否|手册原文，未改动|
|E10 三段式 `for repeat`/`passed`/`assert`|否|手册原文|
|E10 性能统计口径|否|手册第 11 步给定的中位数与比值公式|
|`StudentE9A` 测试选题与断言|**部分**|选题方向（声明变更 / 链式 resolved）由我确定；四条预期由我推导|
|`StudentE10A` 测试选题与断言|**部分**|选题方向（key 粒度：注释 vs 指令）由我确定；两个方向的预期由我推导|
|三次变异检验的设计与执行|否|模型未建议，由我设计|
|报告/ADR 中所有数字|否|全部逐条对照 `$OUT` 下的文件核实|

**拒绝的建议**：模型在 E8 阶段曾建议「直接改仓库 Dockerfile 把 tuna 换成 nju 并合入 main」。本阶段继续沿用拒绝结论，E9/E10 未再触碰 Dockerfile（镜像已建好，源码通过挂载运行，改 `lab.py` 不需要重建镜像）。

**人工修改**：

1. E9 与 E10 的测试预期全部先推导后写断言。E9 的关键推导：改声明行不触及配方，所以 `key` 必相等，`reused` 应为完整两目标，但 `resolved` 仍须按新声明重算。E10 的关键推导：`key['directives']` 只收 `#` 开头行，所以 C 注释不改变 `key`、`#define` 会改变。
2. 三次变异检验由我独立设计与执行，模型未参与：

   |实验|变异点|结果|
   |---|---|---|
   |E8|删 `key.directives`|失败：`'extra.h' not found in ['config.h','main.c']`|
   |E9|复用分支强制 `resolved=[]`|失败：期望两条 MD，实得 `[]`|
   |E10|`directives` 收全文件|失败：`key` 不等断言|

   三处变异均在 `/tmp` 副本执行，原 `lab.py` 未修改，`git status` 每次都只显示 `test_profile.py`。
3. E10 性能表里 `unchanged` 与 `declaration` 的冷启动离群值（0.009075 s、0.005531 s）我选择保留而不剔除，并在报告中显式说明——避免为了「好看的数字」掩盖真实波动。

**实际验证**：

|目的|命令|结果|
|---|---|---|
|E9 第 4–9 步|`lab_python` 各步|`C1_REUSE_PASS` / `C2_REFRESH_PASS` / `C3_RESOLVED_PASS`，STEP_EXIT_CODE 全 0|
|E10 第 8 步|`lab_python` 门禁|`DYNAMIC_CROSSCHECK_AND_MATRIX_PASS`|
|E10 第 9 步|30 行核对|`MATRIX_PASS`，六类各 5|
|全量测试|`unittest discover … test_profile.py`|`Ran 10 tests … OK`，三个定向日志均 `exit=0`|

**贡献边界**：`lab.py`、`run_lab.py`、`environment/` 全部来自分发包，未改动；本人贡献仅 `labs/e8e10/test_profile.py` 中新增的三个 `Student` 类（`StudentE8A` 23 行、`StudentE9A` 47 行、`StudentE10A` 56 行）。

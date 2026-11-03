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

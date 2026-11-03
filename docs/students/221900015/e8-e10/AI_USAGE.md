# AI使用记录

**工具/模型/日期**：CodeBuddy（DeepSeek）· 2026-11-03

**输入上下文与问题**：把课程材料 `DevOps_E8_E10_20261031` 中的 A 组三份操作手册（E8/E9/E10）在本人仓库 `Devops_G10` 的 `student/221900015/e8-e10` 分支上真实跑通，并在不改变验收语义的前提下补充个人测试与文档。

**模型建议**：

1. 把三份手册中的 bash 代码块按章节顺序抽取成单个可执行脚本，替换掉原有的 `read -r -p` 交互行，避免手工逐条粘贴出错。
2. 扩充镜像构建：清华源 403 时改用阿里云源构建同一 Dockerfile 的临时副本。
3. 新增三个测试类：`StudentE8A221900015`（头文件层间接 include 使旧图失效）、`StudentE9A221900015`（body→include→declaration 三连，验证图复用但结论重算）、`StudentE10A221900015`（三级头文件链下增量与全量必须一致）。
4. 建议把 `scan()` 的全局失效键改成按目标局部失效以提升加速比。

**采纳/拒绝及理由**：

- 采纳 1、2、3。1 只改变执行方式，不改变命令内容；2 只替换镜像站地址，Dockerfile 与包集合不变；3 是新增用例，独立预期先于运行写出。
- 拒绝 4。局部失效会让 E9 C2 的 `refreshed={main.o,helper.o}` 断言失败，属于改变手册规定的验收语义；同时新增 `#include` 引用的头文件在旧图中不存在，局部指纹无法在扫描前判断影响面，正确性风险大于收益。核心 `lab.py` 因此保持与 main 一致。

**人工修改**：

- 逐条核对每个 `STEP_EXIT_CODE` 与关键 JSON，确认 `reused/refreshed/added/resolved` 与报告表格一致，未把示例数值当成本次结果。
- 报告中所有 SHA、OUT 路径、耗时均取自本次运行的 `work/` 目录，未使用 `05_来源与验证` 中的参考证据。
- 三个测试类的预期在运行前写在测试注释与报告中，运行后仅核对，未按输出反向修改断言。
- 自查发现首轮报告末节仍是占位符、`work/ci-e8e10/` 未落盘、源码 SHA 与 `OUT/student-source-commit.txt` 不一致，本轮按手册补齐：CI 段改为真实 run/headSha/conclusion/artifact/PR，SHA 拆成“运行基线 + 个人提交”，并重新执行 `gh run view`/`gh run download` 保存运行证据。

**实际验证命令/输入/结果**：

```bash
docker run --rm --network none ... python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v
# Ran 13 tests in 0.476s / OK（原包 7 项 + 同学 3 项 + 本人 3 项）

cat work/e10-A-manual.1kYmmv/matrix/gate.json        # {"track":"A","passed":true,"rows":30}
cat work/e10-A-own.11225683/matrix/gate-own.json    # {"track":"A",...,"passed":true,"rows":5}
cat work/ci-e8e10/<RUN_ID>/run.json                 # 真实 run 元数据（headSha/conclusion/url）
```

**贡献边界**：实验代码（`labs/e8e10/lab.py`）来自课程材料/仓库 main，不是本人重写；本人贡献为在真实环境完成 E8/E9/E10 三轮验证、三个新增测试类、一个自建 E10 场景，以及上述三份文档。AI 助手负责命令编排与文档起草，实测结果与判定由本人复核。

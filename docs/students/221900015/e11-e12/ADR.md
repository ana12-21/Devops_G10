# ADR：集成接口决策

编号：ADR-E11E12-221900015　日期：2026-11-17　作者：221900015（G10，A 组）

## 问题

E8/E9 的产物是“给人看的 JSON + 日志”，E10 的 `patch()/validate()` 要的是“可被程序消费、且能证明自己属于哪次提交”的依赖图。两条轨道之间缺三件事：产物身份（哪次提交、哪个任务）、内容完整性（是不是被换过）、以及跨风格 Makefile 的落点规则。

## 候选方案

1. **直接传递 `scan()` 原始 dict**：字段最少，但没有 commit/job/trace，无法判断报告是否过期，也无法把“补丁打在变量行还是规则行”说清楚。
2. **自定义 protobuf/自定义二进制**：表达力强，但 E10 的 `validate()`、BuildChecker、评审脚本都要跟着改，跨语言成本高。
3. **JSON envelope + `artifact://` URI + sha256**（采用）。

## 采用方案与原因

envelope 固定七字段 `schema_version/job_id/trace_id/kind/commit/status/data/artifacts`：

- `commit` 让“旧报告”成为可判定的错误（`STALE_REPORT`），而不是靠人眼看；
- `artifacts[].sha256` + `artifact://<job>/<相对路径>` 让下游先校验再消费，任务文件接口再按 URI 解析，路径越界直接 404；
- `data` 保留 `scan()` 的原始形状，E8/E9 的字段语义不用翻译，`patch()` 只挑 `MISSING`。

补丁落点按 Makefile 风格分三支（`macro` 追加到变量赋值行、`mixed` 追加到引用 `$(HEADERS)` 的规则行、`direct` 追加到规则行），因为同一份依赖图在三种写法下要改的位置不同；把风格判断放进 `patch()` 而不是让调用方指定，避免“报告和项目对不上”时静默写错行。

## 输入输出字段

输入（`POST /v1/jobs` 的 `input`）：`mode`（e11-a/e11-b/e12）、`repo`、`base`、`target`、`candidate`、`fixed_report`、`expected_output`、`build_timeout`、`idempotency_key`。
输出：`job_id`、`status`、`trace_id`、`stages[].artifact{uri,sha256,bytes}`、`error{code,message}`、`artifacts[]`。

## 兼容性与测试

- 基线提交与目标提交不同是常态，两者都写进结果（`base_commit`、`target_commit`），下游不得假设相同。
- 两类守卫：envelope 校验（`check_envelope`）与 `patch()` 内的 commit 比对，任一层都能单独拦住旧报告（本人的 4 号用例证明第二层独立生效）。
- 网络受限时只替换 candidate 的 apt 源（保留 digest 固定的 `FROM` 与原指令），属于部署适配，不改契约；`work/e11-b-02` 与 `work/e11-b-01` 的对照说明这一点。
- 回归：`run_e11e12.py test` 的 20 个用例覆盖 envelope、路径安全、风格落点、STALE_REPORT、profile 边界。

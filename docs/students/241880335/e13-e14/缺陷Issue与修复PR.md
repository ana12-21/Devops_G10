# 缺陷 Issue 与修复 PR

下面四条记录来自 E13–E14 的实际运行。B 组同学这次缺席，B 组项目相关的条目在「发现方」里注明是 A 组代跑。

## 缺陷 1：教师候选 Dockerfile 的 apt 源在本机房返回 403，三个未知项目和一等样例都构建不起来

### Issue

用例编号与发现方：H1-jsmn、H2-inih、H3-tiny-aes 的原样运行，另波及 `data/integration-sample` 一等样例的 DRAFT 阶段。发现方是 A 组 241880335。

输入仓库及完整 SHA：

- H1-jsmn `948a1d30cd758d32d45a50f788e5a95fb1d89c69`
- H2-inih `3aadb81763c79651e4dfa99b725ba921ee2b8a39`
- H3-tiny-aes `5640bb69a01e64559207e9f74d15a9ae71a4d0f3`
- 一等样例 target `195b84fd5cc0ab7243fd020c02d7e392dfb58e5f`

预期与实际：

预期是 iter-01 报 `MISSING_MAKE`，iter-02 装好 build-essential 之后构建成功，进入五阶段。实际是 iter-01 正常报 `MISSING_MAKE`，iter-02 在 apt 阶段 `exit code 100`：

```
E: Failed to fetch https://mirrors.tuna.tsinghua.edu.cn/debian-security/dists/trixie-security/InRelease  403  Forbidden [IP: 101.6.15.130 443]
E: The repository 'https://mirrors.tuna.tsinghua.edu.cn/debian-security trixie-security InRelease' is not signed.
```

三个项目的外层结果都是 `FAILED` / `DRAFT_FAILED`，job 分别是 `job-955fe26c…`、`job-d10db970…`、`job-5dfbf34d…`。

失败阶段、错误码和原始日志路径：阶段是 `draft` 的 iter-02，外层错误码 `DRAFT_FAILED`，内层 `attempts[1].build_exit_code` 是 100。日志在 `work/e13-H1-jsmn-01/draft-build/iter-02/build-stderr.log`，H2 和 H3 结构相同。

严重度与理由：阻断。它不是代码缺陷，是环境上的镜像源不可用，但它直接挡住了 E13 出口门禁里「三个教师发放项目均有结果」这一项。

最小复现步骤：

```bash
python3 run_e11e12.py run --request data/e13-upstream-student/H1-jsmn/request-e12.json --out work/repro-01
docker run --rm python:3.13-slim python3 -c \
  "import urllib.request;urllib.request.urlopen('https://mirrors.tuna.tsinghua.edu.cn/debian/dists/trixie/Release',timeout=20)"
# 实测返回 HTTP Error 403: Forbidden
```

是否影响其他任务或原仓库：不影响 E11–E12 的既有证据。原先用的 `debian.sources` 直连，这次也没有改动任何已发布的 Dockerfile 和仓库文件，影响范围仅限于 E13/E14 的构建期。

### PR

关联 Issue：本缺陷 1。这批改动还没推送，远端没有 Issue 编号和 PR 记录。

修改文件与原因：

- 新增 `data/e13-upstream-student/{H1-jsmn,H2-inih,H3-tiny-aes}/candidate-local-mirror.Dockerfile`，只把 `https://mirrors.tuna.tsinghua.edu.cn` 换成 `https://mirrors.nju.edu.cn`，其余指令逐字保留，改动一行。
- 新增 `data/e13-upstream-student/*/request-e12-local-mirror.json`，只是把 `candidate` 指向上面那份文件。
- 新增 `data/integration-sample/candidate-local-mirror.Dockerfile`、`data/integration-sample/e12-local-mirror.json`、`data/integration-sample/e11-b-local-mirror.json`，同一处理，用于一等样例。
- 新增 `data/real-candidate.Dockerfile`，A 组真实项目的候选，COPY 清单匹配该项目的 `Dockerfile.broken`，同样只换镜像源。
- 教师原件一个都没改，`candidate.Dockerfile` 的 sha256 都记录在下面。

失败前证据和修复后同一测试的证据：

| 项目 | 失败前 | 修复后 |
| --- | --- | --- |
| H1-jsmn | `FAILED`，`job-955fe26c6cac41f5822dc4165aca306e` | `SUCCEEDED`，`job-824807315d4c4ce8b2f27f84c0ea57ac` / `trace-431566408cd04b808cee2d6dea774984`，177 个产物 |
| H2-inih | `FAILED`，`job-d10db97013ac4a52a910beb0e3a30eba` | `SUCCEEDED`，`job-29ca0fc99af5457ab1cce34bfd752282` / `trace-e17df3f47b414b30897eb27822e82bb5`，177 个产物 |
| H3-tiny-aes | `FAILED`，`job-5dfbf34de17e48c48785667b1dee6feb` | `SUCCEEDED`，`job-fb762da7e2a44e6f87feb188e39f1d62` / `trace-84fdd6b42cd6490ea00dafe4963a78ad`，177 个产物 |
| 一等样例 E11-B | `FAILED`，`job-59ca2e2339c04196b2cd506fb95c23e5`，报 `Docker client command exceeded 600s` | `SUCCEEDED`，`job-2b97ad2d754942c6867ba7bda0cb5fec` / `trace-e17e3ef734704f4b82e80c7ad05a8632`，96 个产物 |

镜像源实测结果：tuna 返回 403；nju、aliyun、ustc 返回 200，nju 实测约 14 MB/s；`deb.debian.org` 约 60 KB/s。

新增或修改的回归测试：没有新增。这个缺陷是环境可达性问题，没有行为回归可言。现有的 `python3 run_e11e12.py test`（13/13）在修复前后都通过，说明修复没有改动任何判定语义。三个教师项目的复跑本身就是端到端回归。

原始仓库修复前后 SHA 核对：

- 教师候选原件（未改动）的 SHA256 分别是 H1 `2ac5ae7cd7e296cb30e78e6f740642b76d8c4286356a2a5ad1dba5d4ebc7a6e7`、H2 `7bf4b0b9861137354132a2a7676b567ec2de1f0ee71161034a27e8a7b06f4e90`、H3 `08305c26b934d66ed96bd0ea149a597fcbe0be23d363511ab75037c51476eee9`。
- 修正版的 SHA256 分别是 H1 `5c9604ba2dfa08795e7f452e0d41b90b42edea32f97a55ca68770d0bdb349c7e`、H2 `76f4e0f0aea9492fcd08cda2ffba454b6a5524e0daa6f66319bbbd5856e950ba`、H3 `f780da2c224904ba98cf1f390ea3577aa126cbe4ae41d6dde2324c7341026c60`。
- A 组 `data/real-project` 的 C0 `f03075f1…`、C1 `94147e8a…`、C2 `89eb38eb…` 三个原始提交都没有改动，`git log` 里仍然可见。

CI 门禁链接与审查人：无。改动没有推送，远端没有 CI 运行记录，审查人待 B 组同学和教师复核。

剩余风险：改用非教师指定的镜像源会改变 apt 包的解析路径，理论上有可能装到不同的小版本。这次三项回归都通过，没有观察到 `build-essential` 版本差异。如果教室网络能直连 `deb.debian.org`，应该优先用教师原件。

## 缺陷 2（适配边界）：B 组的 Dockerfile.broken 与 DRAFT 候选规则不兼容

### Issue

用例编号与发现方：C1 的 A 测 B。发现方是 A 组 241880335（代跑）。

输入仓库及完整 SHA：`data/peer-b-adapted`，target 首次尝试是 `152a3d060ff272a58321e35d3fcbe1f1344f2136`。

预期与实际：

预期是候选 Dockerfile 只要插入一行修复 `make` 缺失的 `RUN` 就能被接受。实际返回 `EXECUTION_FAILED: Candidate changed required project/build/runtime instructions`。

原因有两层。B 组原来的 `Dockerfile.broken` 是 mdfixer 演示版本（`COPY main.c extra.h config.h Makefile ./`、`RUN make main`、`CMD ["./main"]`），而 DRAFT 的 `prepare_candidate()` 要求候选只能在原 `Dockerfile.broken` 的指令序列里插入 `RUN`，不能改 COPY、WORKDIR、CMD。这个 COPY 清单又缺了适配时新增的 `helper.c`，`main` 目标也链接不到 `helper.o`。

失败阶段、错误码和原始日志路径：阶段在 `snapshot` 之后、`draft` 之前。job `job-aeaaed98ea4b445c97bb88ed31dc7b08`，trace `trace-76a13d1a2b6f4fd4b79f14894c9662af`，证据在 `work/e13-c1-a-tests-b-attempt1-EXECUTION_FAILED/`。

严重度与理由：非阻断。属适配范围公告事项，按手册「扩展适配和测试后再评价算法正确性」处理。

最小复现步骤：用 B 组原样 `Dockerfile.broken` 配官方候选，跑 `mode: e11-b`。

是否影响其他任务：不影响 A 组自身项目和教师三个项目，它们的 `Dockerfile.broken` 与 profile 是一致的。

### PR

关联 Issue：本缺陷 2。

修改文件与原因：改的是 `data/peer-b-adapted/Dockerfile.broken`，在适配副本里，B 组上游仓库没有被改动。COPY 清单补上 `helper.c`，`RUN make main` 改成 `RUN make app`，`CMD ["./main"]` 改成 `CMD ["./app"]`。理由和必要性写在 `data/peer-b-adapted/ADAPTATION.md` 里。

失败前和修复后的证据：失败是 `job-aeaaed98…`。修好之后能进入五阶段，随后被缺陷 3 拦在 repair 阶段。检测职责的最终结论看 `work/e13-c1-a-tests-b/`，job `job-8c24c39a95594321870924a08cd575be`，`SUCCEEDED`。

新增或修改的回归测试：没有新增。以 `ADAPTATION.md` 记录适配范围，作为「不支持项公开」的交付物。

原始仓库修复前后 SHA 核对：B 组上游 `f6b8268…` 和 `29d0cb7…` 未改动，适配副本 base 是 `24377c9a…`，target 是 `ece241a7…`。

CI 门禁链接与审查人：无（未推送）。审查人待 B 组确认这个适配是否可接受。

剩余风险：适配把构建入口名从 `main` 改成了 `app`。已经保留 `main: app` 别名，`make main` 仍然可用。

## 缺陷 3（适配边界，已知问题）：lab.validate() 写死 VALUE，宏名是 MESSAGE 的项目在 repair 阶段被拒绝

### Issue

用例编号与发现方：C1 的 A 测 B，用 `mode: e12` 尝试。发现方是 A 组 241880335（代跑）。

输入仓库及完整 SHA：`data/peer-b-adapted`，base `24377c9a923b781fe12a4164771f2673dc4121f7`，target `ece241a75462377e737c9e80c620b8c7aa90e0a0`。

预期与实际：

预期是 draft、full-check、incremental-check、repair、recheck 五个阶段全部成功。实际前四个阶段成功，`validate()` 的 header-change 检查把 `config.h` 覆写成 `#define VALUE 2`，而 B 组 `config.h` 定义的是 `MESSAGE "v1"`，于是 `make app` 报 `main.c:6:20: error: 'MESSAGE' undeclared`，`checks['test']` 为 false，阶段返回 `REPAIR_REJECTED`。

失败阶段、错误码和原始日志路径：阶段是 `repair` 里的 validation，错误码 `REPAIR_REJECTED`，job `job-2942af3036424d4f99815dc4bca86049`，trace `trace-6c9906d3a46d40db85c822fb61f8d3b1`，证据在 `work/e13-c1-a-tests-b-e12-REPAIR_REJECTED/`。

严重度与理由：非阻断。A 组在 C1 的职责是用 BuildChecker/EChecker 测全量和增量检测，修复验证属 B 组 DRAFT/MDFixer。检测路线走 `e11-a`，不受这条影响，已经通过。

最小复现步骤：对任何 `config.h` 的宏名不是 `VALUE` 的项目跑 `mode: e12`。

是否影响其他任务：不影响 A 组真实项目和教师三个项目，它们的 `config.h` 用的都是 `VALUE`，E14 五阶段都通过了。

### 处理方式（不修改代码）

改 B 组业务代码会让被测缺陷本身被抹掉，放宽 `validate()` 会让门禁失去意义，两条都不做。

按职责边界记录结论：A 侧检测通过，修复验证阶段标记为适配范围外。这个情况公开写进了 `交叉测试记录.md` 的「未解决非阻断问题」。

如果后续需要 B 组项目也走完 repair，有两个办法：一是让 B 组在 `config.h` 里同时提供 `VALUE` 和 `MESSAGE`，二是由教师在 `validate()` 里把 header-change 的探针宏名与被测项目解耦。

## 缺陷 4（环境适配，已知问题）：orchestrate.py 要求项目内有 Dockerfile.broken

### Issue

用例编号与发现方：E14 真实项目首跑。发现方是 A 组 241880335。

输入仓库及完整 SHA：`data/real-project`，target 首试用 `94147e8a2559385e6adf0c680837c7033d6df6c2`。

预期与实际：预期直接跑五阶段。实际 `draft` 返回 422，报 `[Errno 2] No such file or directory: '/course/work/e14-real-01/target-project/Dockerfile.broken'`。

失败阶段、错误码和原始日志路径：阶段 `draft`，错误码 `FILENOTFOUNDERROR`，job `job-58b550d1685e433eb75b84b314f8b415`，证据在 `work/e14-real-01-attempt1-NO_DOCKERFILE_BROKEN/`。

严重度与理由：非阻断。E12 的真实项目只用于检测，本来就不需要构建候选入口，E14 才需要这个文件。

最小复现步骤：对没有 `Dockerfile.broken` 的项目跑 `orchestrate.py`。

是否影响其他任务：不影响 E12 的既有证据。

### PR

关联 Issue：本缺陷 4。

修改文件与原因：在 `data/real-project` 的 C1 之上追加一个只新增 `Dockerfile.broken` 和 `.gitignore` 的提交 `b03b828f92d8029f083c270ae652429adb9772a4`，打标签 `e14-broken-b03b828` 固定。C0、C1、C2 三个原始提交保持不变，`main.c`、`Makefile`、`config.h` 都没有触碰，被测的依赖缺陷和程序输出 `1` 都没有变。

失败前和修复后的证据，四次尝试：

| 尝试 | 结果 |
| --- | --- |
| 1. target 用 C1，没有 `Dockerfile.broken` | `FAILED`，`FILENOTFOUNDERROR`，`job-58b550d1685e433eb75b84b314f8b415` |
| 2. 加了文件，但 COPY 里误带了 `extra.h` | `FAILED`，`VALUEERROR: Baseline did not reproduce missing make`，`job-f911da536b9841b88a6f5d693c94e6d9` |
| 3. 候选 COPY 清单仍与 `Dockerfile.broken` 不一致 | `FAILED`，`VALUEERROR: Candidate changed required project/build/runtime instructions`，`job-c1c5243eadc14cb58fa03a4ca3a7d27a` |
| 4. 修正 COPY 清单，并为该项目生成专用候选 `data/real-candidate.Dockerfile` | `SUCCEEDED`，`job-d750c407d0104c5aafcc4a7e3cc42739` / `trace-56ee02a2d6534e87b2fcad49f5304673`，153 个产物 |

新增或修改的回归测试：没有新增。三次失败的目录全部保留，作为同一测试的前后对照。

原始仓库修复前后 SHA 核对：C0 `f03075f1…`、C1 `94147e8a…`、C2 `89eb38eb…` 未变，新增的 `b03b828…` 只包含 `Dockerfile.broken` 和 `.gitignore`。

CI 门禁链接与审查人：无（未推送）。

剩余风险：E12 的真实项目证据指向 `94147e8a…`，E14 指向 `b03b828…`，两者的标注必须分开。本文件和 `候选发布说明.md` 里都是分开列的。

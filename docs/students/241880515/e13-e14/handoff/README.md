# G10 → B10 反向测试交接

提供者为 G10 A 轨杨宗乔，学号 241880515。整理日期为 2026-11-18。请 B10 记录实际执行人、B 轨服务代码完整 SHA、镜像 ID 和执行时间。

## 项目与固定输入

项目来自 G10 仓库 labs/e8e10/environment/fixtures/md-rd，添加 helper.c/helper.o、调用 helper() 并适配 -O0 编译参数。C1 修改函数体，C2 修改头文件包含关系，后续添加 Dockerfile.broken 并对齐基础镜像标签。完整历史保存在 project.bundle。

- base 为 f03075f14ed32fecaa1aeb69dd3fde1edc5c824c。
- target 为 963a143b6ed8d6ba907798b356ff33752b67485a。
- 项目位于 Git 仓库根目录，双 C 源、显式 Make 规则，构建目标 app，运行输出 1。
- 目标提交仍包含 main.o 缺少 config.h 声明的问题。期望修复该缺失依赖，验证接受，复检无 MISSING。
- candidate.Dockerfile 来自 G10 已成功的 E12 输入，固定基础镜像摘要，apt 使用阿里镜像。执行需要 Docker、网络和既有 E11–E12 服务环境。
- fixed-md-from-e12.json 来源于 G10 既有 work/e12-real-02，源任务 job-f7420983a581491f973390c6b5fd829a。该文件用于历史结果复现。本次正式交叉运行的任务号和执行时间请另行记录。

## Windows PowerShell 上传

将本文件夹通过 scp 上传至 B10 自己的仓库 data/g10-from-241880515。使用 B10 的实际 SSH 地址和仓库路径。后续命令均在 Ubuntu 中执行。

## Ubuntu 准备

运行目录为 B10 已配置好 run_e11e12.py 的个人仓库根目录。将交接文件夹放到 data/g10-from-241880515，且 repo 子目录应尚不存在。

```bash
cd data/g10-from-241880515
sha256sum -c SHA256SUMS
git clone project.bundle repo
git -C repo checkout --detach 963a143b6ed8d6ba907798b356ff33752b67485a
git -C repo cat-file -t f03075f14ed32fecaa1aeb69dd3fde1edc5c824c
cd ../..
```

成功标志为哈希检查全部 OK、目标提交正确、基线对象类型输出 commit。

## Ubuntu B 轨复现与完整链路

运行目录仍为 B10 个人仓库根目录。B 轨入口需要支持 fixed-md 信封及 fixed_report_sha256 读取前校验。先核对代码能力，保留当前服务代码 SHA。输出目录需使用新名称。

```bash
git rev-parse HEAD
python3 run_e11e12.py run --request data/g10-from-241880515/request-e11-b.json --out work/e13-B-on-G10-01
python3 run_e11e12.py run --request data/g10-from-241880515/request-e12.json --out work/e13-B-on-G10-e12-01
```

成功标志为退出码 0、result.json 的 status 为 SUCCEEDED、补丁验证 accepted=true、recheck 无 MISSING。E12 应具有 draft、full-check、incremental-check、repair、recheck 五阶段，repair 消费本轮增量报告。

## 回传材料

请回传两次请求、完整结果目录、执行人、服务代码完整 SHA、镜像 ID 和时间。保留失败尝试及其日志。若还未执行某项，请标记未执行。B 轨消费本次另一份 G10 检测 B10 项目的报告时，请继续使用原交接规定的 B10 目标提交，两套项目的请求和报告分别存放。

# BuildChecker 服务（E4 骨架）

本仓库在 E4 中建立可重复环境，E5 起在 `services/buildchecker/` 中实现论文方法。

## 第一次使用

```sh
mkdir -p ~/<学号> && cd ~/<学号>
git clone <本组仓库地址> && cd <仓库>
git config user.name  "<学号>"        # 统一用学号；服务器账号是共用的，不要加 --global
git config user.email "<学号>@localhost"  # E4 不推送，填本地示例值即可
make all
```

`git remote -v` 应指向真正的本组远程仓库。课堂试跑所用的 `/root/E4实验包/A-buildchecker` 只是本地模板；从它克隆不会自动同步到课程平台。共享服务器上的学号目录与 Git 身份只隔离个人工作和标记未来的提交，运行 `make all` 本身不会产生 Git 提交。

## 命令

| 命令 | 作用 | 证据（work/<时间>/） |
| --- | --- | --- |
| `make doctor` | 服务器与 Git 身份自检 | env.json |
| `make build` | 构建服务镜像 | build.log、image.json、toolchain.lock |
| `make test` | 容器内运行单元测试 | test.log |
| `make smoke` | 用 E3 样例做冒烟测试 | smoke.json |
| `make scan` | 密钥检查（工作区、Git 历史、镜像） | secret-scan.txt |
| `make all` | 以上五步 | 同一个证据目录 |
| `make shell` | 进入服务容器；仓库的 `work/` 挂到容器的 `/app/work`，在那里保存的文件退出后仍保留 | — |
| `make lock` | 修改 requirements-dev.in 后重新生成锁文件 | requirements-dev.lock |

预期：`make test` 全部通过；`make smoke` 输出 `"passed": true`，strace 记录中能看到 `config.h` 被打开，`app_output` 为 `1`；`make scan` 显示"未发现问题"。

## 约定

- 基础镜像按 digest 固定，升级时只改 `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` 一行，并在提交说明中写明新 digest。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。

# 相对 data/integration-sample/candidate.Dockerfile 的唯一改动：
#   apt 源由 deb.debian.org 改为 mirrors.nju.edu.cn（本机房访问 deb.debian.org 约 60KB/s，
#   83MB 的 build-essential 会超过 build_timeout=600s；nju 实测约 14MB/s）。
# 其余指令与原始候选完全相同。
FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY main.c helper.c config.h extra.h unused.h Makefile ./
RUN sed -i "s|http://deb.debian.org|https://mirrors.nju.edu.cn|g" /etc/apt/sources.list.d/debian.sources && apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 update && apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
RUN make app
CMD ["./app"]

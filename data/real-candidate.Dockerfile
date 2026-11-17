# A 组（241880335）真实项目的构建候选。
# 规则：只能沿用该项目 Dockerfile.broken 的指令序列，并插入修复「基础镜像无 make」的 RUN。
# 插入的 RUN 把 apt 源换到 mirrors.nju.edu.cn（本机房 deb.debian.org 约 60KB/s，
# 83MB 的 build-essential 会超过 build_timeout=600s；nju 实测约 14MB/s）。
FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
RUN sed -i "s|http://deb.debian.org|https://mirrors.nju.edu.cn|g" /etc/apt/sources.list.d/debian.sources && apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 update && apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY main.c helper.c config.h unused.h Makefile ./
RUN make app
CMD ["./app"]

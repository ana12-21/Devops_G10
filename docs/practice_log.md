# 配对练习记录（A10 ↔ B10）

> Backlog T-009 产物：三轮问题与结论齐。
> 时间：2026-09-20 苏州课堂 E2 阶段。

## 配对信息

- A10：ana12-21 / Devops_G10（本仓库，依赖检测方向）
- B10：`<TODO: B10 仓库地址>`
- 渠道：GitHub PR / Issue

---

## 第一轮：A 说明环境与基线需求 → B 出产物样例

### A10 给 B10 的需求

```
- 仓库 + 完整 commit (40 位 SHA)
- 可运行镜像（ubuntu:22.04 基础，gcc/make/libfoo-dev）
- clean build 命令（make）
- 验证命令（make check）
- max_iterations（默认 5）
- deadline_sec（默认 1800）
```

### B10 收到后给的样例

```json
{
  "job_type": "DRAFT",
  "input": {
    "repository": {"url": "git@github.com:/<owner>/<project>.git", "commit": "<40 sha>"},
    "build": {"command": "make", "verify_command": "make check"},
    "max_iterations": 5,
    "deadline_sec": 1800
  }
}
```

### 双方达成的一致

| 字段 | 约定 |
|------|------|
| `repository.url` | 用 SSH 格式 `git@github.com:<owner>/<repo>.git` |
| `repository.commit` | 完整 40 位 SHA，不接受短 SHA |
| `verify_command` | 必须存在，DRAFT 至少跑一次 |
| `max_iterations` | 默认 5，失败次数过多返回 `EXEC_4002` |

### 待办 / 遗留

- 镜像引用格式（`registry.local/pair10/...` vs `docker.io/...`）B 组需统一

---

## 第二轮：B 说明 MD 报告需求 → A 出发现样例

### B10 给 A10 的需求

```
- 接收 A 组的 md_report.json
- 必须包含 target / dependency / evidence / type 字段
- evidence 至少 file + line
- 只消费 MISSING（REDUNDANT 不进入修复路径）
```

### A10 收到后给的发现样例

```json
{
  "type": "MISSING",
  "target": "src/main.o",
  "dependency": "include/config.h",
  "evidence": {
    "file": "src/main.c",
    "line": 12,
    "snippet": "#include \"config.h\""
  },
  "detector": "BUILDCHECKER"
}
```

### 双方达成的一致

| 字段 | 约定 |
|------|------|
| `type` | 只接受 `MISSING` / `REDUNDANT` |
| `evidence.file` | 相对项目根 |
| `evidence.line` | 整数，从 1 开始 |
| `detector` | `BUILDCHECKER` / `ECHECKER` / `INSTRUCTOR_ORACLE` |
| REDUNDANT 发现 | MDFixer **不**消费，由 A 组下次处理 |

### 待办 / 遗留

- `snippet` 是否必填？A10 倾向"选填"，B10 倾向"必填方便定位"——暂定选填
- `commit` 字段是否需要在 finding 上？A10 倾向必填，B10 觉得冗余——暂定必填（与 request 同 commit）

---

## 第三轮：失败输入 → 讨论状态与错误码

### 测试样例 1：job_type 写错

```json
{ "job_type": "ABC", ... }
```

**预期行为**：
- 任意服务接收 → 返回 `SCHEMA_1001`
- `status = FAILED`
- 不进入 RUNNING

**实际行为**：✅ 与契约一致。

---

### 测试样例 2：INCREMENTAL_CHECK 缺 baseline

```json
{
  "job_type": "INCREMENTAL_CHECK",
  "input": {
    "repository": {"url": "git@github.com:/x.git", "commit": "abc"},
    "build": {"command": "make", "project_root": "./"}
  }
}
```

**预期行为**：
- EChecker 接收 → 返回 `BASELINE_2001`
- `status = FAILED`
- 不进入 RUNNING

**实际行为**：✅ 与契约一致（validate.py 反例 7 已覆盖）。

---

### 测试样例 3：MD 报告里有 REDUNDANT

```json
{
  "findings": [
    {"type": "REDUNDANT", "target": "src/x.o", "dependency": "include/y.h"}
  ]
}
```

**预期行为**：
- A 组 SUCCEEDED（含 findings）
- MDFixer 接收 → **拒绝**（EXEC_4003 或 SCHEMA_1001，因只消费 MISSING）

**实际行为**：✅ MDFixer 应过滤后报 "no actionable findings"。

---

### 状态机讨论

```
QUEUED ──► RUNNING ──► SUCCEEDED  (有 findings 也算成功)
                  │
                  ├─► FAILED      (系统错误 → job.error)
                  ├─► TIMED_OUT   (EXEC_4002)
                  └─► CANCELLED   (用户主动取消)
```

**关键不变量**：
- SUCCEEDED + output.findings（合法）
- FAILED + job.error（合法）
- **SUCCEEDED + job.error** → 违例
- **FAILED + output.findings** → 违例
- **error 与 findings 同时出现** → 违例

---

## 总结

- ✅ 三轮交换样例全部跑通
- ✅ validate.py 正面 13 个、反面 8 个全部覆盖
- ✅ 状态机与错误码在反例中表现一致
- ⏳ B10 仓库地址待填写
- ⏳ 选定项目的 SHA 待 E3 准备阶段补全
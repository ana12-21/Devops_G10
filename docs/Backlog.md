# Backlog（A10 组）

| ID     | 任务                       | 责任方       | 产物                              | 验收条件                                    |
|--------|----------------------------|--------------|-----------------------------------|---------------------------------------------|
| T-001  | 统一 Job 模型定义          | A/B 共同     | `contracts/task.schema.json`      | 四类 `job_type` 都能套用                    |
| T-002  | BuildChecker 请求/响应样例 | A 组         | `contracts/full_check.*.json`     | validate.py 通过                            |
| T-003  | EChecker 请求/响应样例     | A 组         | `contracts/incremental_check.*.json` | 缺 `baseline` 时被拒绝                   |
| T-004  | 错误码定义                 | A/B 共同     | `contracts/error_codes.md`        | 至少覆盖 6 类错误                           |
| T-005  | 产物 URI 格式约定          | A/B 共同     | `contracts/artifact_format.md`    | A、B 两组都能照此生成                       |
| T-006  | 选定分析项目 + C0/C1/C2    | A 组         | `data/commits.md`                 | 3 个完整 40 位 SHA，可独立 checkout         |
| T-007  | ADR-001 异步 Job 决策      | A/B 共同     | `docs/ADR-001.md`                 | 含 context/decision/alternatives/consequences |
| T-008  | 与 B10 对接契约            | 配对组       | `contracts/draft.req.json` 等     | B10 在 PR 上确认                            |
| T-009  | 配对练习三轮记录           | 配对组       | `docs/practice_log.md`            | 三轮问题与结论齐                            |
| T-010  | E3 前安装 BuildChecker     | A 组个人     | 本地 `bc --version` 可用          | 能跑通 `bc analyze <repo> <commit>`         |

> 状态：T-001 ~ T-005 已完成草稿；T-006 课前完成；T-008、T-009 课堂完成。
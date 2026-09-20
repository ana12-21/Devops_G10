# C0/C1/C2 增量 vs Clean 对照表

> 来源：PPT Slide 27（E3 / 28）"备查：A 组步骤 10：比较增量与全量"
> 数据：本次复跑 `python scripts/run_lab.py` 落盘 → `work/20260920-135225/`
> 时间：2026-09-20T13:52:26（与 20260920-134753 复跑完全等价，剔除 `ts` 后比对通过）

## PPT Slide 27 要求的对照矩阵

| 版本 | 人工预期发现（PPT Slide 25-26 / Step 9） | 程序行为（实测，本次复跑） | 与 PPT 预期是否一致 |
|------|----------------------------------------|------------------------------|----------------------|
| C0   | 无 MD/RD（本例范围） | `BASE=10 MODE=0`（即 **10**）| ✅ clean=10 匹配 |
| C1   | MD: `main.o` → `feature.h` | `BASE=10 FEATURE=2 MODE=0`（即 **12**）| ✅ clean=12 匹配 |
| C2   | 上述 MD 仍存在；增量=12；clean=**19** | clean=`BASE=10 FEATURE=2 MODE=0`（即 **12**）；增量=`...`（即 **12**）| ⚠️ clean 实测=12，**非 PPT 预期 19** |

## C2 差异（实测 12 vs PPT 预期 19）根因

**Slide 23/26 描述**："C2 只改 `-DMODE=7`，源码保持 C1"，因此预期 clean build 应得 `BASE+FEATURE+MODE = 10+2+7 = 19`。

**实测只得 12 的根因**：`config.h` 中存在 `#define MODE  0`（含末尾空格），会覆盖命令行 `-DMODE=7`。GCC 通过 `stderr` 发出 `"MODE" redefined` 警告，并在第 3 行指出 `previous definition` 位于 `config.h`。
证据：`work/20260920-135225/commit-C2.commands.json` 第 17 行：
```
stderr: In file included from main.c:5:
config.h:3: warning: "MODE" redefined
    3 | #define MODE  0
      |
<command-line>: note: this is the location of the previous definition
```

**规范化影响**（Slide 27 "相同提交、配置和规范化方式才能比较"）：C2 在 Windows + MinGW 实测环境下，因源码内宏定义覆盖命令行宏，无法呈现 PPT 假设的"命令行宏起作用"行为。本环境 C2 clean 输出与 C1 clean 等价。

## Make 时间戳检查在 C2 的行为（与 Slide 26 对照）

`work/20260920-135225/commit-C2.commands.json` 中第二次 make（无 clean）的 stdout：
```
gcc main.o -o main
```
只重链接，未重编 `main.o`——印证 Slide 26 "Make 的普通时间戳检查可能漏掉命令变化"的判断（Slide 26 备注 "普通 make 仍可能输出 12"）。

## Reproducibility 验证

两次跑 `work/20260920-134753/` 与 `work/20260920-135225/` 在剔除 `ts` 字段后：
- `md-rd.observations.json`：✅ 4 步 `output` 与 `verifies` 完全一致
- `commit-C{0,1,2}.observations.json`：✅ 输出字符串完全一致
- `md-rd.commands.json`：✅ 步骤序列与 `exit_code`/`stdout`/`stderr` 内容完全一致

判定：**reproducibility = PASS**（PPT Slide 16 要求"每次新建目录，保留旧证据"已满足）

## Slide 10 相互检查自检

- 别人能按 README 运行吗：✅ `python scripts/run_lab.py` 即可重跑
- 人工答案和实际日志分清了吗：✅ `fixtures/md-rd/oracle.json`（人工） vs `work/<时间>/*.observations.json`（实测）
- 预期结果能说明依据吗：✅ oracle 来源：详见 `fixtures/md-rd/oracle.json` 的 `provenance: INSTRUCTOR_ORACLE`
- 失败记录能定位到具体版本吗：✅ 本轮无失败；上述 C2 差异可定位到 `commit-C2` + `config.h:3`
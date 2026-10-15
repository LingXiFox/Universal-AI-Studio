# 分层测试与 CI 验收

当前支持目标：**macOS 26.2+、Apple Silicon arm64**。稳定 Xcode 优先；`macos-26` Runner 固定 Xcode 26.6。macOS 27 使用本机已有 beta 工具链做独立兼容验证，不替代稳定工具链检查。旧版 macOS 14／15／26.0／26.1 不在支持范围。

## 状态与报告规则

| 状态 | 含义 |
|---|---|
| 通过 / passed | 对当前 commit 实际执行，断言与命令全部成功 |
| 失败 / failed | 构建、断言、校验或执行失败，必须让 CI 失败 |
| 跳过 / skipped | 已存在的测试或步骤因条件未运行，不计入通过 |
| 未执行 / not executed | 尚未安排或缺少设备／模型／权限，不表示支持 |
| 尚未覆盖 / not covered | 当前没有对应实现或测试，不能用空测试填充 |

本轮不开发模型管理、下载器、任务系统、资源策略、API 或任何推理后端。它们没有现成测试可运行，必须在 CI Summary 列为尚未覆盖。仅证明 App 配置、构建、工具脚本正确，不证明产品功能已完成。

## Level 1：每次 Push／Pull Request 的常规 CI

入口：`.github/workflows/ci.yml`；本地等价检查：

```sh
bash Scripts/check.sh
```

CI 使用全新 `macos-26` arm64 Runner 和干净 checkout，不恢复 SwiftPM 或构建缓存。执行顺序：

1. 检查 Runner 是 macOS 26／arm64，选定稳定 Xcode 26.6，记录 OS／Swift／SDK；构建目录不得事先存在。
2. `swift package resolve`，当前依赖清单为空，但解析步骤仍须真实执行。
3. 执行所有 Python unittest 和所有 Swift XCTest；Swift 输出 xUnit XML，Python 输出逐项状态和总数。
4. 分别构建 Debug／Release，并检查真实 App 可执行文件、签名、bundle 类型与架构。
5. 同时核对 Package.swift、Info.plist 的 `LSMinimumSystemVersion` 和 Mach-O `LC_BUILD_VERSION.minos`，三者必须都是 26.2；二进制只能包含 arm64。
6. 无论成功或失败，上传运行日志、xUnit、bundle 检查 JSON 和已成功生成的 App tar 包，保留 14 天。写入 Summary 的步骤结果与 GitHub outcome 一致。

测试失败后仍尽可能执行独立的构建步骤，但不用 `continue-on-error`、`|| true` 或条件退出 0 隐藏失败。`tee` 管道使用 `pipefail`。因依赖解析失败而未执行的构建写为 skipped；原始失败仍让整个 job 失败。

当前测试清单：

| 范围 | 当前可执行测试 | 当前边界 |
|---|---|---|
| Swift 配置契约 | 2 项 XCTest：最低系统、原生 bundle 元数据 | 不等于模型业务逻辑测试 |
| 开发脚本／产物契约 | 6 项 Python unittest，含旧部署目标／Intel／通用二进制／错误 Mach-O 平台的拒绝用例 | 正向真实产物在每次构建后另外检查 |
| 模型元数据解析与管理 | 尚未覆盖 | Phase 2 模块尚未实现 |
| 下载器／下载任务／恢复 | 尚未覆盖 | Phase 2 模块尚未实现 |
| 任务状态／资源管理规则 | 尚未覆盖 | Phase 1 模块尚未实现 |
| API 协议 | 尚未覆盖 | Phase 5 模块尚未实现 |

新建上述模块时，同一变更须加入纯 Swift 逻辑测试，并直接纳入不带筛选的 `swift test`，不得新增默认跳过的业务测试。在模块尚未实现的 Phase 0，不提前写业务接口或虚构测试成功。

## Level 2：轻量真实推理

**当前：未执行／尚未覆盖。没有已接入后端，也没有已验证极小模型。** 本轮不下载权重，不安装运行时，不用硬编码回答作为推理证据。

首次后端接入时必须交付以下可运行内容，再宣称 Level 2 可执行：

1. 模型清单：官方来源、固定 revision、许可证、文件大小／SHA-256、实际验证设备与后端版本。禁止自动执行仓库远程代码。
2. 将真实加载／推理／卸载测试加入独立 integration target 或脚本，记录命令、总下载量、超时与失败退出码。首轮预算建议权重总量不超过 100 MiB、总下载不超过 200 MiB、单次 120 秒；若后端没有这种模型，记录实际最小路径并说明预算调整。
3. 断言模型确实加载、输出来自实际后端且满足与任务相关的基本有效性要求，验证错误输入与卸载；禁止用固定结果代替计算。
4. 在能运行该后端的执行环境中触发；云端无法取得 GPU／内存时明确未执行。模型下载／推理失败是失败，不自动转成 skip。

普通 CI 不为不存在的后端制造“集成测试通过”。Level 2 暂缺不阻塞 Phase 1；进入相应后端里程碑时必须补齐。

## Level 3：真实 Apple Silicon GPU

**当前：未执行／尚未覆盖。未接入 MLX／Metal 后端。** `macos-26` Runner 的 arm64 CPU 身份不能作为真实 GPU 推理通过的证据。本轮提供验收流程，尚无可以声称已运行的 GPU 测试命令。

后端到位后，在授权使用的实体 Apple Silicon 设备上按下列步骤重复执行：

| 步骤 | 干什么 | 如何验收与留证 |
|---|---|---|
| G1 | 固定源码、工具链、模型和环境 | 记录 commit、硬件／内存、系统／Xcode／SDK、后端版本、模型 revision／校验、供电与温度状态；确认存在可用 Metal 设备 |
| G2 | 记录空闲基线并加载模型 | 预热后采样空闲资源；真实加载，记录耗时、App 与后端内存／GPU 占用；只有成功取得后端模型句柄才算加载成功 |
| G3 | 执行固定输入的真实推理 | 保存输入、输出和耗时／吞吐量，确认 GPU 后端实际执行；输出按任务断言，不仅检查非空日志 |
| G4 | 取消运行中任务 | 在运行中取消，确认输出停止、任务进入取消态、无继续写结果；随后新任务仍可完成 |
| G5 | 注入可控错误 | 使用专用副本模拟缺文件／坏输入／后端错误，拒绝真实耗尽主机内存；错误可恢复且不误报成功 |
| G6 | 卸载与释放 | 记录卸载时间和卸载后至少 30 秒的资源轨迹，确认模型引用和执行任务清除；区别可回收缓存与泄漏，记录不能立即归零的分配器行为 |
| G7 | 重复与归档 | 同设备同配置至少 3 轮，保存每次值、中位数与失败；任何一项未执行就单独标记，不汇总成全绿 |

第一条真实后端测试到位时，必须将上述 G2–G6 的实际可运行命令写入本文件，并在 `Docs/Verification/` 提交结果。本轮不添加会直接返回成功的 GPU 占位脚本。

## Level 4：完整多模态端到端

由 Phase 3 分模态逐步增加，不要求每次 Push 下载大型模型。每个模态必须提供固定模型／输入、真实产物、GUI 与后端执行证据、取消／失败／释放验证和复现命令。

| 方向 | 最小真实证据 | 本轮状态 |
|---|---|---|
| LLM | 多轮流式回答、token／延迟 | 尚未覆盖 |
| VLM | 实际图片输入和相应视觉回答 | 尚未覆盖 |
| Embedding | 真实向量、维度及相似度 | 尚未覆盖 |
| Reranker | 真实分数和候选排序 | 尚未覆盖 |
| 图像生成 | 可解码图片和生成参数 | 尚未覆盖 |
| 图像编辑 | 原图、编辑目标及真实结果 | 尚未覆盖 |
| ASR | 音频、转录和时间戳 | 尚未覆盖 |
| TTS | 文本与可播放的真实合成语音 | 尚未覆盖 |
| 视频生成 | 真实生成并播放的视频 | 尚未覆盖 |
| 音乐生成 | 真实生成并试听的音频 | 尚未覆盖 |

各模态阶段验收与正式发布前运行完整回归；未完成真实路径不能被“编译通过”替代。未执行的大模型任务不阻塞无关的 Phase 1 工作。

## 性能保留与比较

原始 Phase 0 三轮数据永久保留在 [初始本地记录](Verification/Phase_0_Local.md)，不得覆盖最快或最慢轮次。新的结果另建带日期／commit 的记录，用同一硬件、OS／工具链、构建模式、窗口状态、采样长度、模型和参数比较。

```sh
bash Scripts/build-app.sh release
mkdir -p .tmp
/usr/bin/python3 Scripts/measure-baseline.py --seconds 30 > .tmp/baseline-release.json
```

至少执行 3 次；采样脚本自动记录硬件型号／内存、系统 build、Xcode 和 Swift 版本。若环境不同，只能并列观察，不计算“性能提升”结论。共享 Runner 的构建或测试耗时不能作为正式性能基准。

| 指标 | 记录口径 | 当前状态 |
|---|---|---|
| App 空闲内存 | Release、预热 5 秒、采样 30 秒；RSS 中位数／峰值 | 已建立初始基线 |
| CPU | 采样期间累计 CPU 时间差／墙钟时间，100% 为一颗核心 | 已建立初始基线 |
| 启动 | 进程创建至根视图 onAppear；不是第一帧或磁盘冷启动 | 已建立初始基线 |
| 模型加载／卸载 | 后端真实 ready／释放完成的耗时，明确缓存状态 | 未执行，后端未实现 |
| 推理吞吐量 | 文本 tokens/s，其他模态用样本／秒或生成时长比；记录预热与参数 | 未执行，后端未实现 |
| 卸载后的资源释放 | App／后端 RSS 与 GPU／内存压力时序，至少 30 秒 | 未执行，后端未实现 |

结果记录须含“通过／失败／跳过／尚未覆盖”和原始数据位置；正式资源判断还需实体设备的 Instruments／系统指标，不能只依赖 RSS。

## 尚需真实硬件验收

- macOS **26.2 实机**的安装、启动、退出与权限行为；CI 的 macOS 26.x 构建不能冒充精确 26.2 实机验收。
- macOS 27 的持续兼容检查；本机结果仅代表当前 beta 系统／工具链。
- 已接入后端后的 Level 2／3 GPU、取消、错误、模型卸载及资源释放。
- 各模态 Level 4、不同内存档位、长期稳定性与能耗。

后面三类随功能阶段补齐，不作为 Phase 1 开工阻塞。Developer ID 签名／公证属于发布阶段，本地 ad-hoc 签名不能代替。

## 官方依据

- [GitHub Runner 规格与架构](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [macOS 26 arm64 镜像与 Xcode 清单](https://github.com/actions/runner-images/blob/main/images/macos/macos-26-arm64-Readme.md)
- [actions/checkout](https://github.com/actions/checkout) 与 [actions/upload-artifact](https://github.com/actions/upload-artifact)：使用已核查的固定 commit，不引入本地依赖。
- [SwiftPM 测试命令实现与 xUnit 支持](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/Commands/SwiftTestCommand.swift)

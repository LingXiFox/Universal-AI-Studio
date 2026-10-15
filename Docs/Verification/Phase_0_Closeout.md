# Phase 0 收尾与 CI 验收

日期：2026-10-15（Asia/Shanghai）。本轮只调整部署要求、建立 CI／测试分层，不提前开发任何后续模态。

## 部署与本地结果

- 正式要求为 **macOS 26.2+、仅 arm64**；不再要求兼容 macOS 14／15／26.0／26.1。
- Package.swift、Info.plist 和本地 Debug／Release Mach-O `LC_BUILD_VERSION.minos` 均实测为 26.2，二进制只含 arm64；签名与 bundle 校验通过。
- 本机 macOS 27.2／Xcode 27.2 beta／Swift 6.4 上，6 项 Python 测试和 2 项 Swift XCTest 通过；Release App 的实际窗口内容经 AX 验证，Command-Q 后进程退出。
- 本机只有 beta Xcode；稳定工具链验收在远程 `macos-26` arm64 Runner 使用固定 Xcode 26.6 完成，不为此安装新本地运行环境。
- 本轮变更前的已验证备份：`/tmp/uas-phase0-before-20261015-114858.tar`。用户验收前保留。

## 远程 CI

私有仓库：[LingXiFox/Universal-AI-Studio](https://github.com/LingXiFox/Universal-AI-Studio)。工作流：[Phase 0 CI](https://github.com/LingXiFox/Universal-AI-Studio/actions/workflows/ci.yml)。

**实际远程验收通过：** [CI run 38678956260](https://github.com/LingXiFox/Universal-AI-Studio/actions/runs/38678956260)，对应源码 commit `e1945daea935ed493d0a44bc47d6f26ba36583b2`，由 Push 自动触发，结论 `success`。

| 远程检查 | 实测 |
|---|---|
| Runner | macOS 26.6.2（25G83），Darwin arm64，全新 checkout，无旧 `.build` |
| 稳定工具链 | Xcode 26.6（17F113），Swift 6.3.3，macOS SDK 26.5 |
| 干净依赖解析 | `swift package resolve` 成功，无缓存恢复，当前零第三方依赖 |
| Python 单元测试 | 6 项通过、0 失败、0 跳过 |
| Swift XCTest | 2 项通过、0 失败、0 跳过；下载后的 XCTest XML 确认有 2 个实际 testcase |
| Debug App | 构建／签名／bundle 检查通过，仅 arm64，plist 与 Mach-O minos 均 26.2 |
| Release App | 构建／签名／bundle 检查通过，仅 arm64，plist 与 Mach-O minos 均 26.2 |
| 结果归档 | Summary、测试日志、真实 XCTest XML、bundle JSON 与两种 App tar 包上传成功，保留 14 天 |

第一次运行 `38678723466` 的构建与测试虽通过，稳定 SwiftPM 却只生成了 0 用例的 Swift Testing XML；它不作为最终报告验收依据。已依据上游确认的问题改用 `--parallel --num-workers 2`，并要求 XCTest 报告包含实际 testcase；空报告拒绝检查也已在本地做正反向验证。修正后的第二次远程运行及下载报告均通过。未采用 Swift Testing 的额外 XML 仍可能为 0，不将其计为额外测试。

工作流配置已启用 Push 和 Pull Request，支持手动触发；本轮实际验证的是 Push 事件，没有为了验收另建占位 PR。测试步骤或构建失败会保留失败结论；归档步骤使用 `always()`，不会把先前失败变成成功。

## 测试边界

| 类别 | 当前状态 |
|---|---|
| 本地当前适用单元测试 | 8 项通过，0 失败，0 跳过 |
| 远程当前适用单元测试 | 8 项通过，0 失败，0 跳过 |
| 模型管理／元数据解析 | 尚未覆盖，模块未实现 |
| 下载器／下载任务 | 尚未覆盖，模块未实现 |
| 任务状态／资源规则／API 协议 | 尚未覆盖，模块未实现 |
| Level 2 真实推理 | 未执行／尚未覆盖，没有已接入后端或已验证极小模型 |
| Level 3 GPU | 未执行／尚未覆盖，未接入 MLX／Metal 后端 |
| Level 4 十类多模态端到端 | 未执行／尚未覆盖，随模态开发补齐 |

完整清单、状态含义、GPU 可重复验收流程见 [分层测试](../Testing.md)。本轮没有模型下载或推理占位成功结果；后续真实推理验证不阻塞 Phase 1。

## 性能与硬件边界

最初的三轮 [Phase 0 基线](Phase_0_Local.md) 保留不变。本轮在同一实体 Mac17,4／32 GiB／macOS 27.2 build 26B5112a／Xcode 27.2 beta／Swift 6.4 上以 Release 重复三轮，每轮预热 5 秒、采样约 30 秒。[完整新测量数据](phase0-closeout-baseline.json) 包含工具链与每轮数值，对应 App 源码 commit `1bad9a13859dda120497780a66295519373859ff`。

| 轮次 | 启动至根视图 ms | 采样 s | RSS 中位数 MiB | RSS 最大值 MiB | CPU %（一颗核心） |
|---|---:|---:|---:|---:|---:|
| 1 | 124.26 | 30.34 | 124.26 | 124.34 | 0.10 |
| 2 | 112.85 | 30.34 | 96.91 | 129.30 | 0.10 |
| 3 | 113.74 | 30.34 | 96.97 | 129.45 | 0.10 |
| 本轮中位数 | 113.74 | 30.34 | 96.97 | 129.30 | 0.10 |
| 初始基线中位数 | 153.07 | 30.33 | 128.34 | 128.48 | 0.10 |

窗口状态、系统缓存和内存回收未严格固定，因此这是观察对照，不据此宣称性能提升，也未设虚构通过阈值。启动指标仍不是第一帧；RSS 不等于物理 footprint。不使用共享 Runner 的耗时作为正式性能结论。模型加载／卸载、推理吞吐量和卸载后资源释放因后端未实现而未执行。

仍需真实硬件验收：精确 macOS 26.2 系统的安装／启动／权限行为，后续后端 GPU、取消／异常／释放，以及各模态真实模型、不同内存档位和长期稳定性。CI 产物声明 26.2 不等于这些实机路径已经通过。

## 收尾结论

本轮 Phase 0 的 macOS 26.2 arm64 部署配置、稳定工具链远程构建、当前适用测试、真实产物检查与报告归档已通过。可以推进 Phase 1；以上真实硬件／推理项目保持未执行或尚未覆盖，不算作已通过，也不等待大型模型来阻塞后续框架开发。

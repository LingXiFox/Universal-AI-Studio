# 开发环境与日常验证

核查日期：2026-10-15（Asia/Shanghai）。产品依据：[开发计划书](AA/Universal_AI_Studio_Project_Plan.md)。

## 1. 当前技术选择

| 项目 | 当前方案 | 边界 |
|---|---|---|
| 平台 | macOS 26.2+，仅 Apple Silicon arm64 | macOS 26.2 为正式最低要求；macOS 27 保持独立兼容验证 |
| 语言 | Swift 6 language mode；manifest tools version 6.0 | Swift 6.0 是工程下限声明，不代表已在该版本验收 |
| UI | SwiftUI；后续必要时 AppKit | 当前只有真实可启动的初始化窗口 |
| 工程 | Swift Package Manager executable target | 暂不建立第二套 Xcode 工程配置 |
| 打包 | 系统 bash、plutil、codesign | 本地 ad-hoc 签名；没有 Developer ID 签名或公证 |
| 脚本检查 | Xcode 提供的 `/usr/bin/python3` 标准库 unittest | 仅开发工具需要 Python；App 不依赖 Python |
| 推理依赖 | 无 | 不预装 llama.cpp、MLX、Diffusers、MCP、模型权重 |
| 持久化／网络服务 | 无 | 不扫描用户目录、不创建模型库、不监听端口 |

零第三方包使 Phase 0 可直接使用现有工具链。选择 SwiftPM 是当前最小方案；沙盒、商店发布、entitlement、复杂资源和运行时分发在相关步骤重新评估，不能把本地打包当作正式发行能力。

## 2. 本机核查结果

| 检查 | 实际结果 |
|---|---|
| 架构 | arm64 |
| 统一内存 | 32 GiB |
| macOS | 27.2，build 26B5112a |
| 开发目录 | `/Applications/Xcode-beta.app/Contents/Developer` |
| Xcode | 27.2，build 27B5028f |
| Swift | Apple Swift 6.4，swiftlang-6.4.0.34.1 |
| macOS SDK | 27.2 |
| Git | 2.56.0 |
| 脚本 Python | `/usr/bin/python3` 3.9.6 |

本机只有 beta 工具链，用于 macOS 27 兼容验证。不切换系统 `xcode-select`，不安装其他 SDK／编译器。常规 CI 固定稳定 Xcode 26.6；其他机器优先选择已安装的稳定 Xcode，通过单条命令的 `DEVELOPER_DIR` 指定。macOS 14／15／26.0／26.1 已移出支持范围。

## 3. 在另一台 Mac 准备环境

先检查，缺失时再由维护者确认安装 Apple 官方 Xcode 和首次启动组件；不要把安装、接受许可或切换全局开发目录藏在脚本里。

```sh
uname -sm
sw_vers
xcode-select -p
xcodebuild -version
swift --version
xcrun --show-sdk-version
git --version
/usr/bin/python3 --version
```

预期：macOS 26.2+、Darwin arm64，稳定 Xcode 优先，Swift 至少 6.0，macOS SDK 不低于 26.2，系统 Python 可运行 unittest。只有 Command Line Tools 或版本满足不能替代真实构建验收。若选择另一套已安装 Xcode，可在单条命令前设置 `DEVELOPER_DIR`，无需修改全局配置。

将项目放入本地可写目录后，在根目录执行：

```sh
bash Scripts/check.sh
open "dist/debug/Universal AI Studio.app"
```

验收：6 项 Python 工具测试与 2 项 Swift 配置测试通过，Debug／Release 各构建并生成 App，plist 和 ad-hoc 签名验证通过；二进制仅含 arm64，Package.swift、plist 与 Mach-O 的最低系统版本均为 26.2；窗口显示“开发环境已就绪”和功能尚未实现的提示，窗口缩放正常，Command-Q 后 App 进程消失。

## 4. 目录与操作约定

```text
Package.swift                         唯一构建 manifest
Sources/UniversalAIStudio/            原生 App 入口与初始化视图
Resources/Info.plist                  App bundle 元数据
Scripts/build-app.sh                 构建、打包、ad-hoc 签名
Scripts/check.sh                     无交互的本地／CI 检查入口
Scripts/measure-baseline.py          Release 启动与空闲采样
Scripts/verify-app.py                manifest／plist／Mach-O／架构／签名检查
Tests/test_development_tools.py      开发脚本回归测试
Tests/UniversalAIStudioTests/        Swift 配置契约测试
.github/workflows/ci.yml             macOS 26 arm64 远程 CI
Docs/AA/                            原始产品计划，保持原文
Docs/Verification/                  人工与真实运行验收记录
dist/{debug,release}/                可再生成的 App
.build/                             SwiftPM 可再生成产物
.tmp/                               临时日志、探针、原始测量结果
```

不直接修改 `dist/` 中的可执行文件或 plist；修改对应源文件后重建。重建会覆盖同配置的开发 App，运行中的开发 App 应先正常退出。正式用户文件和模型不得放入这些构建目录。

## 5. 检查与性能口径

`bash Scripts/check.sh` 运行依赖解析、shell 语法检查、全部 Python unittest、全部 Swift XCTest、Debug／Release 构建与真实 bundle 校验，以及工作区／暂存区差异检查。`verify-app.py` 同时读取真实 Mach-O `LC_BUILD_VERSION.minos`、Info.plist 与解析后的 Package.swift；只改 plist 无法通过。报告保存在 `.tmp/reports/`。当前 Swift 测试覆盖真实配置，模型管理／下载／任务／API 模块尚未实现，相关业务测试在 CI Summary 标为尚未覆盖；四层测试规则见 [分层测试](Testing.md)。

性能记录使用 Release，不将 Debug 与 Release 混比：

```sh
mkdir -p .tmp
/usr/bin/python3 Scripts/measure-baseline.py --seconds 30 > .tmp/baseline-release.json
```

测量脚本只启动并终止自己的子进程。先等待根视图 `onAppear` 标记，预热 5 秒，再每秒采样一次，默认 30 秒，可指定 1–300 秒。每次测量前退出手动打开的同名 App；测量时保持窗口可见，避免其他高负载操作。脚本不判断遮挡状态。

- `startup_to_root_view_ms`：从创建进程到收到根视图回调标记的时间，**不等于首帧呈现时间，也不是磁盘冷启动时间**。
- `rss_median_mib`／`rss_max_mib`：BSD `ps` 的 RSS 统计，不等于物理 footprint 或整个系统 GPU／共享内存占用。
- `cpu_mean_percent_one_core`：采样期间累计 CPU 时间差 / 墙钟时间 × 100；100% 表示占满一颗核心，不是整机百分比。
- 本脚本未测 GPU、电源、内存压力、Swap 或推理开销。正式性能评估须结合 Instruments／系统工具，并分别记录 App 与运行时子进程。

每次至少重复 3 次，保留设备、工具链、构建模式、采样长度、每次值与中位数；只有一次观测时不得当作稳定指标。原始探针与日志放 `.tmp/`，归纳后的可信结果放 `Docs/Verification/`。

## 6. CI 与发布边界

GitHub 私有仓库为 `LingXiFox/Universal-AI-Studio`，已获许可使用 GitHub Actions。工作流在 Push／Pull Request 自动触发，使用 `macos-26` arm64 Runner 与稳定 Xcode 26.6；不恢复缓存，先解析依赖，再执行全部当前适用单元测试与 Debug／Release 构建。日志、xUnit、bundle JSON 和 App tar 包无论成功或失败均尝试保留 14 天。测试失败会让工作流失败，不用 `continue-on-error` 隐藏。实际运行链接及状态以 [收尾记录](Verification/Phase_0_Closeout.md) 为准。

GUI 启动退出、真实模型、故障恢复和性能验收不能由编译结果代替；无桌面的 CI 不应声称完成 GUI 验收。当前 App 的 ad-hoc 签名仅供本地开发，不能作为跨机器发行包。

## 7. 常见失败处理

| 现象 | 处理 |
|---|---|
| Xcode 未选定／许可未接受 | 记录 `xcode-select -p` 和错误，由维护者完成 Apple 工具链准备后重试；不自动提权 |
| SwiftPM 产物目录变化 | 使用 `swift build -c … --show-bin-path`，不硬编码 `.build/arm64-*` |
| App 拒绝启动／签名失败 | 重新运行打包脚本，检查其 `codesign` 输出；不移除 quarantine、不禁用 Gatekeeper |
| 采样 20 秒内没有根视图标记 | 先手动打开 App 检查桌面会话与崩溃；该次记失败，不填 0 |
| 最低系统或稳定 Xcode 失败 | 保留失败环境和日志，修复兼容性或经确认调整支持声明 |

## 8. 查询依据

接口与命令已用本机 `swift build --help`、实际编译及官方资料交叉核对：

- [SwiftPM 官方文档](https://docs.swift.org/main/documentation/packagemanagerdocs/)
- [SwiftPM 构建配置说明](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/UsingBuildConfigurations.md)
- [SwiftPM 6.4 产物路径变化](https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/ReleaseNotes/6.4.md)
- [Apple WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)

后续运行时的版本、许可证、API 和支持模型尚未选定，实施时依据当时官方文档核验，不把候选框架视作已兼容。

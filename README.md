# Universal AI Studio

面向 Apple Silicon 的 macOS 原生多模态本地 AI 工作台。目前仅完成开发工程初始化，模型管理、下载、推理、Agent 和 API 尚未实现。

## 开发入口

使用已安装的 Xcode／Apple 工具链，不需要 Homebrew 安装步骤或第三方包。工程为 Swift Package + SwiftUI App，构建脚本生成可由 Finder 打开的 `.app`；当前没有 `.xcodeproj`。后续需要签名能力、沙盒或复杂资源管理时，再评估是否增加 Xcode App target。

```sh
# 在项目根目录执行；路径包含空格时务必使用引号。
bash Scripts/check.sh
open "dist/debug/Universal AI Studio.app"

# 单独构建 Release
bash Scripts/build-app.sh release

# 测量 Release 基线，脚本结束后会关闭其启动的进程。
/usr/bin/python3 Scripts/measure-baseline.py --seconds 30
```

可用 `open Package.swift` 在 Xcode 中阅读／调试源码；Finder 启动验收使用打包后的 App。脚本参数只接受 `debug` 或 `release`，默认 `debug`。

## 文档

- [产品计划书](Docs/AA/Universal_AI_Studio_Project_Plan.md)：完整产品范围与 Phase 0–7 要求。
- [开发环境](Docs/Development_Environment.md)：版本、命令、验证边界和日常工作方式。
- [分步实施与验收](Docs/Implementation_Plan.md)：每一步做什么、如何验收、保留什么证据。
- [Phase 0 本地验收记录](Docs/Verification/Phase_0_Local.md)：本机实测结果与尚未验证的项目。

`dist/`、`.build/`、`.tmp/` 均为可再生成内容，不提交 Git。没有模型下载、后台服务或外部运行时自动安装行为。

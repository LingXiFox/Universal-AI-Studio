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

状态：工作流已配置，正在进行第一次远程运行验收；运行成功之前不标记通过。最终 commit、运行链接、结果和测试报告将在实际结果返回后补充。

## 测试边界

| 类别 | 当前状态 |
|---|---|
| 本地当前适用单元测试 | 8 项通过，0 失败，0 跳过 |
| 远程当前适用单元测试 | 等待实际 CI 结果 |
| 模型管理／元数据解析 | 尚未覆盖，模块未实现 |
| 下载器／下载任务 | 尚未覆盖，模块未实现 |
| 任务状态／资源规则／API 协议 | 尚未覆盖，模块未实现 |
| Level 2 真实推理 | 未执行／尚未覆盖，没有已接入后端或已验证极小模型 |
| Level 3 GPU | 未执行／尚未覆盖，未接入 MLX／Metal 后端 |
| Level 4 十类多模态端到端 | 未执行／尚未覆盖，随模态开发补齐 |

完整清单、状态含义、GPU 可重复验收流程见 [分层测试](../Testing.md)。本轮没有模型下载或推理占位成功结果；后续真实推理验证不阻塞 Phase 1。

## 性能与硬件边界

最初的三轮 [Phase 0 基线](Phase_0_Local.md) 保留不变。本轮同一实体 Mac 上的 Release 复测数据将在采样完成后追加；不使用共享 Runner 的耗时作为正式性能结论。模型加载／卸载、推理吞吐量和卸载后资源释放因后端未实现而未执行。

仍需真实硬件验收：精确 macOS 26.2 系统的安装／启动／权限行为，后续后端 GPU、取消／异常／释放，以及各模态真实模型、不同内存档位和长期稳定性。CI 产物声明 26.2 不等于这些实机路径已经通过。

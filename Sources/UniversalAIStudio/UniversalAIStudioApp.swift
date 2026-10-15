import SwiftUI

@main
struct UniversalAIStudioApp: App {
    var body: some Scene {
        WindowGroup("Universal AI Studio") {
            VStack(spacing: 12) {
                Image(systemName: "cpu")
                    .font(.system(size: 48))
                    .foregroundStyle(.tint)
                    .accessibilityHidden(true)
                Text("Universal AI Studio")
                    .font(.largeTitle)
                Text("开发环境已就绪")
                    .font(.title3)
                Text("当前为原生工程初始化版本，模型与推理功能尚未实现。")
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .textSelection(.enabled)
            }
            .padding(40)
            .frame(minWidth: 540, minHeight: 360)
            .onAppear {
                // Measure view lifecycle readiness, not the first rendered frame.
                if ProcessInfo.processInfo.environment["UAS_MEASURE_STARTUP"] == "1" {
                    FileHandle.standardOutput.write(Data("UAS_ROOT_VIEW_APPEARED\n".utf8))
                }
            }
        }
        .defaultSize(width: 860, height: 560)
    }
}

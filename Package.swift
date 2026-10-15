// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "UniversalAIStudio",
    platforms: [.macOS(.v14)],
    products: [.executable(name: "UniversalAIStudio", targets: ["UniversalAIStudio"])],
    targets: [.executableTarget(name: "UniversalAIStudio")]
)

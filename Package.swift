// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "UniversalAIStudio",
    platforms: [.macOS("26.2")],
    products: [.executable(name: "UniversalAIStudio", targets: ["UniversalAIStudio"])],
    targets: [
        .executableTarget(name: "UniversalAIStudio"),
        .testTarget(name: "UniversalAIStudioTests", path: "Tests/UniversalAIStudioTests")
    ]
)

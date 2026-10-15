import Foundation
import XCTest

final class ConfigurationTests: XCTestCase {
    private func appInfo() throws -> [String: Any] {
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        let data = try Data(contentsOf: root.appendingPathComponent("Resources/Info.plist"))
        return try XCTUnwrap(PropertyListSerialization.propertyList(from: data, format: nil) as? [String: Any])
    }

    func testMinimumSystemVersion() throws {
        XCTAssertEqual(try appInfo()["LSMinimumSystemVersion"] as? String, "26.2")
    }

    func testNativeAppBundleIdentity() throws {
        let info = try appInfo()
        XCTAssertEqual(info["CFBundleExecutable"] as? String, "UniversalAIStudio")
        XCTAssertEqual(info["CFBundlePackageType"] as? String, "APPL")
        XCTAssertEqual(info["CFBundleSupportedPlatforms"] as? [String], ["MacOSX"])
    }
}

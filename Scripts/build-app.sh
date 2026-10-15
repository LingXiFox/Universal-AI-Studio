#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
configuration="${1:-debug}"
case "$configuration" in
    debug|release) ;;
    *) echo "Usage: $0 [debug|release]" >&2; exit 2 ;;
esac
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
    echo "This development build requires macOS on Apple Silicon." >&2
    exit 1
fi

swift build -c "$configuration" --product UniversalAIStudio
bin_path="$(swift build -c "$configuration" --show-bin-path)"
app="dist/$configuration/Universal AI Studio.app"
mkdir -p "$app/Contents/MacOS"
cp "$bin_path/UniversalAIStudio" "$app/Contents/MacOS/UniversalAIStudio"
cp Resources/Info.plist "$app/Contents/Info.plist"
/usr/bin/plutil -lint "$app/Contents/Info.plist"
/usr/bin/codesign --force --sign - "$app"
/usr/bin/codesign --verify --strict "$app"
echo "Built: $app"

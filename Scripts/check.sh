#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

cd "$(dirname "$0")/.."
for script in Scripts/*.sh; do bash -n "$script"; done
/usr/bin/python3 -m unittest discover -s Tests -p 'test_*.py' -v
for configuration in debug release; do
    bash Scripts/build-app.sh "$configuration"
    app="dist/$configuration/Universal AI Studio.app"
    test -x "$app/Contents/MacOS/UniversalAIStudio"
    test "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$app/Contents/Info.plist")" = UniversalAIStudio
    test "$(/usr/bin/lipo -archs "$app/Contents/MacOS/UniversalAIStudio")" = arm64
done
git diff --check
git diff --cached --check
echo "Development checks passed. GUI acceptance is a separate manual check."

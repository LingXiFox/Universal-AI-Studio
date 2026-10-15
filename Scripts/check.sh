#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

cd "$(dirname "$0")/.."
mkdir -p .tmp/reports
for script in Scripts/*.sh; do bash -n "$script"; done
swift package resolve
/usr/bin/python3 -m unittest discover -s Tests -p 'test_*.py' -v
swift test --xunit-output .tmp/reports/swift-tests.xml
for configuration in debug release; do
    bash Scripts/build-app.sh "$configuration"
done
git diff --check
git diff --cached --check
echo "Development checks passed. GUI acceptance is a separate manual check."

#!/bin/zsh
# Run tests on the "iPhone 16" simulator (ZMYUSIC_SIM_NAME picks another one, e.g. a second
# simulator kept for tests so the app on your everyday one isn't replaced). Extra arguments go to xcodebuild, e.g.
#   scripts/sim-test.sh -only-testing:ZMyusicTests
#   scripts/sim-test.sh -only-testing:LyricsTests/LrcParserTests
# Building happens in parallel with other checkouts; the simulator run itself is
# serialised through a lock file so concurrent checkouts don't fight over the device.
set -euo pipefail
# Parallel compile jobs are capped at 3 so the machine stays usable during a build (JOBS=n overrides).
export DEVELOPER_DIR=${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}
cd "$(dirname "$0")/.."
DEST="platform=iOS Simulator,name=${ZMYUSIC_SIM_NAME:-iPhone 16}"
LOCK="${ZMYUSIC_SIM_LOCK:-${TMPDIR:-/tmp}/zmyusic-sim.lock}"
xcodebuild build-for-testing -workspace ZMyusic.xcworkspace -scheme ZMyusic \
  -destination "$DEST" -derivedDataPath .derived -jobs "${JOBS:-3}" -quiet
lockf -t 3600 "$LOCK" xcodebuild test-without-building -workspace ZMyusic.xcworkspace \
  -scheme ZMyusic -destination "$DEST" -derivedDataPath .derived -jobs "${JOBS:-3}" "$@"

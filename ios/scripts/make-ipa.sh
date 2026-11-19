#!/bin/zsh
# Build a Release IPA for testers to sideload (AltStore, SideStore, Sideloadly, …): the app and its
# two extensions, ad-hoc signed with their entitlements so the sideloader re-signs them with the
# tester's own Apple ID and remaps the shared app group. No Apple Developer account is needed here.
#   scripts/make-ipa.sh            → build/Myusic-<version>-<build>.ipa
# JOBS=n caps parallel compile jobs (default 3), as in the other scripts.
set -euo pipefail
export DEVELOPER_DIR=${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}
cd "$(dirname "$0")/.."

DERIVED=.derived-release
xcodebuild build -workspace Myusic.xcworkspace -scheme Myusic -configuration Release \
  -destination 'generic/platform=iOS' -derivedDataPath "$DERIVED" -jobs "${JOBS:-3}" -quiet \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY=""

APP="$DERIVED/Build/Products/Release-iphoneos/Myusic.app"
[ -d "$APP" ] || { echo "no app at $APP" >&2; exit 1; }
VERSION=$(/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" "$APP/Info.plist")
BUILD=$(/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "$APP/Info.plist")

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/Payload"
cp -R "$APP" "$STAGE/Payload/"
STAGED="$STAGE/Payload/Myusic.app"

# Inside out: embedded frameworks, then each extension with its entitlements, then the app.
find "$STAGED" -name "*.framework" -type d -prune | while read -r fw; do
  codesign --force --sign - --timestamp=none "$fw"
done
codesign --force --sign - --timestamp=none --entitlements App/Config/MyusicWidget.entitlements \
  "$STAGED/PlugIns/MyusicWidgetExtension.appex"
codesign --force --sign - --timestamp=none --entitlements App/Config/MyusicShare.entitlements \
  "$STAGED/PlugIns/MyusicShareExtension.appex"
codesign --force --sign - --timestamp=none --entitlements App/Config/Myusic.entitlements "$STAGED"

mkdir -p build
OUT="build/Myusic-$VERSION-$BUILD.ipa"
rm -f "$OUT"
(cd "$STAGE" && zip -qry - Payload) > "$OUT"
echo "$OUT ($(du -h "$OUT" | cut -f1))"
scripts/verify-ipa.sh "$OUT"

Android, Windows, Linux, macOS and iOS builds, all produced from this tag by GitHub Actions. The IPA is unsigned on purpose: AltStore, SideStore or your own Ad Hoc profile signs it, because ZMyusic is not on the App Store.

| Platform | File |
|---|---|
| Windows 10/11 x64 | `ZMyusic-<version>-windows-x64-setup.exe`, `.msi`, or the portable ZIP |
| Linux x86_64 | `ZMyusic-<version>-linux-x86_64.AppImage`, `.deb` or `.rpm` |
| macOS 13+ | `ZMyusic-<version>-macos-arm64.dmg` (Apple Silicon) or `-macos-x64.dmg` (Intel) |
| Android 8+ phone/tablet | `ZMyusic-<version>-android-phone-arm64-v8a.apk`, or `-universal` |
| Android TV | `ZMyusic-<version>-android-tv-arm64-v8a.apk`, or `-universal` |
| Wear OS 3+ | `ZMyusic-<version>-android-wear.apk` |
| iPhone / iPad (iOS 17+) | `ZMyusic-<version>-ios-unsigned.ipa` |

The APKs are signed and install over an older ZMyusic of the same flavor. The watch app only pairs with the phone app signed by the same key. The IPA is unsigned: AltStore, SideStore or an Ad Hoc profile signs it with your own Apple ID.

macOS builds are unsigned unless a Developer ID is configured: right-click the app and choose Open the first time, or run `xattr -cr /Applications/ZMyusic.app`. The Windows installer is unsigned too: SmartScreen shows "Windows protected your PC", so choose More info, then Run anyway.

Support: https://saweria.co/latiefahmad

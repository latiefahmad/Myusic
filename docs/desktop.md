# Desktop

The desktop app is a JVM Compose window around the same `shared` and `sharedUi`
modules the phone uses. Windows, Linux and macOS build from the same source;
only the natives and the installer change.

## Requirements

| Platform | JDK | Native tools |
|---|---|---|
| Windows 10/11 x64 | 21 | MSYS2/MinGW `g++`, Ninja, CMake (optional: without them there is no Automix and no native frame/SMTC) |
| Linux x86_64 | 21 | `g++`, Ninja, CMake, DBus (MPRIS and the Secret Service) |
| macOS 13+ | 21 | Xcode command line tools (clang), CMake |

The JDK is a hard requirement: `desktopApp` targets JVM 21 bytecode and the
packaged runtime is a jlink image of it.

## Run and package

```bash
./gradlew :desktopApp:run
./gradlew :desktopApp:packageDistributionForCurrentOS
```

`packageDistributionForCurrentOS` maps to `packageMsi`/`packageExe` on Windows,
`packageDeb`/`packageRpm` on Linux, and `packageDmg` on macOS. Output lands in
`desktopApp/build/compose/binaries/main/`.

A Windows folder that runs without an installer, for checking a build on
another machine, is `./gradlew :desktopApp:windowsPortable`; it verifies the
Compose runtime, the Windows Skiko renderer and the Windows FFmpeg natives are
actually inside the archive.

| Variable / property | Effect |
|---|---|
| `-Pmyusic.version=1.9.1` | Public version, overriding the root `myusicVersionName` |
| `-Pmyusic.target=windows\|linux\|macos` | Cross-configure the build for another OS |
| `local.properties`: `LASTFM_API_KEY`, `LASTFM_SECRET` | Scrobbling and Last.fm sign-in |
| `local.properties`: `LISTEN_TOGETHER_SERVER` | Party server, when not using the default |
| `local.properties`: `MODULE_INDEX_URL` | Addon index override |

## What is native

- **Automix** - `desktopApp/native/CMakeLists.txt` compiles the same C++ the
  Android app uses. The library is packaged under `native/` and unpacked to
  `~/.local/share/myusic/analysis` on first use. Without a compiler the app
  still runs and Automix is simply absent.
- **Windows media controls and frame** - `native/smtc` (WinRT SMTC) and
  `native/window` (DWM frame), both built with MinGW. Without them the app uses
  Compose's own window decoration and has no SMTC entry.
- **PoToken** - JavaFX's WebKit runs BotGuard, the same job the Android WebView
  does. The JavaFX jars carry natives per platform (`win`, `linux`, `mac` /
  `mac-aarch64`).
- **Audio** - FFmpeg (JavaCPP) decodes and resamples; Java Sound is the output.
  There is no exclusive/bit-perfect path on desktop, so the player reports the
  mixer's format rather than claiming bit-perfect output.

## macOS

- `TargetFormat.Dmg` produces a `.app` inside a DMG. `bundleID` is
  `com.music.myusic`, the icon is `packaging/icons/AppIcon.icns`.
- Compose desktop uses the system window frame on macOS, so the Windows frame
  bridge is not built.
- Unsigned builds need `xattr -cr /Applications/Myusic.app` or a right-click
  Open on first launch. `MACOS_CERTIFICATE`, `MACOS_CERTIFICATE_PASSWORD` and
  `MACOS_SIGNING_IDENTITY` in the release workflow sign the bundle; without
  them the DMG ships unsigned.
- Chromium cookie import reads the browser key from the login Keychain with
  `security(1)`. Firefox import needs nothing beyond the profile.
- There is no MPRIS or SMTC equivalent yet: Now Playing integration is a known
  gap, tracked in `docs/platform-matrix.md`.

## Linux

- MPRIS is spoken directly over DBus; the Secret Service holds the Discord
  token and Last.fm session. Both are skipped gracefully when the session bus
  is absent (a bare X session, a container).
- `packaging/icons/AppIcon.png` is the launcher icon for the DEB/RPM.

## Settings

`java.util.prefs` under the node `com.music.myusic.desktop`: the registry on
Windows, `~/.java/.userPrefs` on Linux, `~/Library/Preferences` on macOS.
Unpacked natives and Automix results live in
`$XDG_DATA_HOME/myusic` (default `~/.local/share/myusic`) on every platform.
Browser profiles and downloaded tracks are stored outside the JDK preferences,
beside the user's music folder.

## Known gaps

| Gap | Why |
|---|---|
| Browser sign-in (opening Chrome for you) | Windows only: the loopback-debugging flow is built around Chromium on Windows |
| Tray icon | StatusNotifierItem covers Linux; AWT/menu-bar icons for Windows and macOS are still to do |
| Now Playing | MPRIS on Linux, SMTC on Windows; macOS has no bridge yet |
| Automix without a compiler | Native build is skipped rather than bundled prebuilt |

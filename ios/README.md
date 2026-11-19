<div align="center">

<br/>

<img src=".github/assets/icon.png" alt="Myusic app icon" width="160" />

# Myusic for iOS

### A YouTube Music client for iPhone and iPad, the iOS app of the Myusic family

<br/>

[![Release](https://img.shields.io/github/v/release/latiefahmad/Myusic?style=for-the-badge&labelColor=0d1117&color=2563eb)](https://github.com/latiefahmad/Myusic/releases)
[![License](https://img.shields.io/github/license/latiefahmad/Myusic?style=for-the-badge&labelColor=0d1117)](LICENSE)
[![Platform](https://img.shields.io/badge/iOS-17%2B-0d1117?style=for-the-badge)](#requirements)

<br/>

[Install](#install) · [Features](#features) · [Building from source](#building-from-source) · [Contributing](#contributing) · [Credits](#credits) · [Disclaimer](#disclaimer-and-legal-notice)

</div>

> [!IMPORTANT]
> Myusic is not affiliated with, endorsed by, or connected to YouTube, Google or Apple in any way. Use it at your own discretion.

---

## What this is

This is the iPhone and iPad app of [Myusic](https://github.com/latiefahmad/Myusic), a YouTube Music client for Android, the desktop and iOS. It is a native SwiftUI app that follows the Android app screen for screen, currently tracking Myusic for Android 1.9.1.

Myusic for iOS began as [BitChord for iOS](https://github.com/maanya145/BitChord-iOS), the SwiftUI port of [BitChord for Android](https://github.com/kushagrasinghx/BitChord) by [Kushagra Singh](https://github.com/kushagrasinghx). The original copyright notices and the GPLv3 licence stay in place; the Android app in this repository is now the reference for every module here.

Where iOS cannot do what Android does, the port uses the closest iOS equivalent or leaves the feature out. The [porting notes](docs/PORTING.md) list each feature, the Android source it comes from, and the tests that cover it.

<!-- Screenshots: no iOS screenshots exist yet. Add them here once taken. -->

## Features

### Playback

- Search, browse and play the YouTube Music catalogue: Home, Explore, moods and genres, artist, album and playlist pages.
- Separate streaming quality for Wi-Fi and mobile data, plus a Dolby Atmos option.
- Optional add-on sources for lossless and Atmos streams, with YouTube Music as the fallback. Sources can be added, tested and reordered.
- Crossfade from 0 to 12 seconds, and Automix, which plans each transition from the beat grid and vocal activity of both tracks.
- Loudness normalization, skip silence, stereo widening and a built-in equalizer.
- A sleep timer: 15, 30, 45 or 60 minutes, or the end of the current track.
- An on-device song cache with an adjustable size limit.
- Stats for nerds on the now playing screen: codec, bitrate and the audio pipeline.

### Lyrics

- Synced lyrics with line and word highlighting, gathered from several providers: LRCLIB, Musixmatch, Genius, KuGou, PaxSenix, BetterLyrics, BiniLyrics, LyricsPlus, SimpMusic, Unison, Megalobiz and YouTube Music.
- Choose and reorder providers, adjust the timing offset, and translate lyrics into another language.
- Share selected lines as an image card.
- Lyrics are kept on the device per track.

### Library and offline

- Sign in with a Google account for your YouTube Music library, playlists and history. You can add several accounts and switch between personal and brand profiles.
- Download tracks for offline play, with metadata and lyrics written into the file.
- Import your own audio files from the Files app.
- Play music from SMB and WebDAV shares on your network.
- Export and import settings and listening history as a JSON file.

### Look and feel

- Animated cover art from Apple Music, Tidal, Spotify and a community index, on the player and on the lock screen.
- Player colours and background taken from the album artwork.
- A landscape player layout and iPad support.
- Five app icons to choose from in Settings.
- The interface is available in 16 languages.

### Social and integrations

- Listen Together: host a listening party and invite others with a code, a link or a QR code.
- Replay: listening statistics by period, with a shareable poster.
- Scrobbling to Last.fm and ListenBrainz.
- Discord Rich Presence with in-app Discord sign-in, showing the track, artist, progress and audio quality.

### System

- Lock screen and Control Center controls.
- Three Home Screen widgets, in small and medium sizes.
- A Share extension that opens YouTube and YouTube Music links in Myusic.
- App Intents for playback.
- A CarPlay interface. It needs Apple's CarPlay audio entitlement, which the project does not carry.

## Requirements

- iPhone or iPad running iOS 17 or later.
- A sideloading tool such as AltStore or SideStore. Myusic is not on the App Store.

## Install

Myusic is not on the App Store: Apple rejects third-party YouTube clients under
Guideline 5.2.3, and the app is GPLv3. Install it with AltStore, SideStore or
any tool that signs an IPA with your own Apple ID.

1. Download the `Myusic-<version>-ios-unsigned.ipa` artifact from a successful
   run of the **iOS** workflow (Actions → iOS → Unsigned IPA), or from
   [Releases](https://github.com/latiefahmad/Myusic/releases) when it is attached
   there.
2. Open it in AltStore or SideStore and sign it with your Apple ID.
3. Install it, then trust the developer certificate under Settings → General → VPN & Device Management.

Building it yourself from Xcode is in the next section. An Ad Hoc or TestFlight
build works the same way once your certificate and provisioning profile are
configured.

To update, install the new version over the old one. Downloads, library and settings carry over.

## Building from source

### What you need

- A Mac with Xcode 26 or newer (the icon assets are Icon Composer files).
- An Apple ID if you want to run the app on a device. The simulator needs no signing setup.

### Open the project

```sh
git clone https://github.com/latiefahmad/Myusic.git
cd Myusic/ios
open Myusic.xcworkspace
```

Open the workspace, not the `.xcodeproj`. It contains the app project and the `MyusicKit` package. Pick the `Myusic` scheme. Xcode resolves the two Swift package dependencies on first open.

### Signing for a device

The project uses automatic signing with no team set, and the maintainer's identifiers. To run on your own device:

1. Select your team under Signing & Capabilities for the `Myusic`, `MyusicWidgetExtension` and `MyusicShareExtension` targets.
2. Change the bundle identifiers to a prefix you own. The app is `com.music.myusic`, the widget is `com.music.myusic.widget` and the Share extension is `com.music.myusic.share`. The extensions must keep the app's identifier as their prefix.
3. Change the app group `group.com.music.myusic` in the three files under `App/Config/*.entitlements` and in `App/Shared/SharedConstants.swift`. The widget and the Share extension read the app's data through this group.

Do not commit these changes in a pull request.

### Optional keys

The app reads two optional build settings, `LASTFM_API_KEY` and `LASTFM_API_SECRET`, into its `Info.plist`. Without them the app builds and runs, but Last.fm sign-in and scrobbling and the genre chart in Replay stay unavailable. To use them, get a key from [Last.fm](https://www.last.fm/api/account/create) and pass both on the command line:

```sh
xcodebuild -workspace Myusic.xcworkspace -scheme Myusic \
  -destination 'generic/platform=iOS Simulator' \
  LASTFM_API_KEY=your_key LASTFM_API_SECRET=your_secret build
```

In Xcode, add them as user-defined build settings on the `Myusic` target, and keep them out of commits. No `.xcconfig` file is attached to the project.

The PaxSenix lyrics key is entered in the app under the lyrics sources, not at build time.

### Command line

The scripts in `scripts/` wrap the common builds. They can be run from any directory.

```sh
scripts/kit-test.sh                      # MyusicKit tests on the Mac, no simulator
scripts/kit-test.sh --filter LyricsTests # one module's tests
scripts/kit-build-ios.sh                 # compile MyusicKit for the iOS Simulator
scripts/app-build.sh                     # compile the app, extensions and test bundles
scripts/sim-test.sh                      # run the Myusic test plan on the "iPhone 16" simulator
scripts/make-ipa.sh                      # build an unsigned Release IPA in build/
scripts/verify-ipa.sh build/<file>.ipa   # check an IPA's signature and app-group entitlements
```

The scripts use `/Applications/Xcode.app` unless `DEVELOPER_DIR` is set. `JOBS=n` sets the number of parallel compile jobs. `MYUSIC_SIM_NAME` picks a different simulator for `sim-test.sh`, and extra arguments go to `xcodebuild`, for example `scripts/sim-test.sh -only-testing:MyusicTests`.

Tests that call real services are skipped unless `MYUSIC_LIVE_TESTS=1` is set, so the default run works offline.

## Project layout

```
Myusic.xcworkspace      open this
App/
  Myusic.xcodeproj      app, widget, Share extension and app-hosted test targets
  Myusic/               the SwiftUI app: screens, navigation, CarPlay, App Intents
  MyusicWidget/         Home Screen widgets
  MyusicShare/          Share extension
  Shared/                 code compiled into the app and both extensions
  MyusicTests/          app-hosted unit and view model tests
  MyusicUITests/        UI and end-to-end tests
  Config/                 Info.plists and entitlements
  Myusic.xctestplan     the scheme's test plan: MyusicTests and every MyusicKit test target
  MyusicE2E.xctestplan  the UI tests, some of which need the network
MyusicKit/              Swift package with all non-UI logic, one module per subsystem
  Sources/
    MyusicCore          shared models, settings, HTTP and logging
    InnerTube             YouTube Music API client, parser and Google sign-in
    StreamResolution      turns a video id into a playable audio stream
    Sources               add-on and JioSaavn sources, matching and fallback to YouTube
    PlaybackQueue         queue, shuffle, autoplay, history and sleep timer
    PlaybackPolicy        quality choice, upgrades, fallbacks and stats for nerds
    Playback              the AVPlayer engine, crossfade and system media controls
    AudioCache            on-disk cache for streamed audio
    AudioDSP              equalizer, loudness, skip silence and spatial audio
    Automix               transition planning with the beat and vocal models
    AutomixAnalyzer       C++ audio analyzer behind a C header
    Lyrics                lyrics providers, parsing, storage and translation
    Downloads             offline downloads, tagging and Files imports
    NetworkLibrary        SMB and WebDAV libraries
    ListenTogether        Listen Together client and invite links
    Integrations          Last.fm, ListenBrainz and Discord
    Replay                listening statistics and backup
    Canvas                animated cover art lookups
    Theming               colours taken from artwork
    MyusicTestSupport     test helpers, never shipped
  Tests/                  one test target per module
scripts/                  build, test and packaging scripts
docs/PORTING.md           feature checklist and porting decisions
```

The top of `MyusicKit/Package.swift` lists the Android source each module ports. Android paths in code comments are relative to [`app/src/main/java/com/music/myusic/`](https://github.com/latiefahmad/Myusic/tree/main/app/src/main/java/com/music/myusic) in this repository.

## Contributing

Contributions are welcome. Read the [contributing guide](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md) before you open a pull request. Pull requests target `main`. For anything larger than a bug fix, open an issue first.

## Credits

### Myusic for Android

Myusic is a rebrand of [BitChord](https://github.com/kushagrasinghx/BitChord) by [Kushagra Singh](https://github.com/kushagrasinghx), licensed under GPL-3.0. The design, the features and most of the behaviour come from that project, and the Android app in [this repository](https://github.com/latiefahmad/Myusic) is the reference for every module here. If you like the app, support the [original project](https://github.com/kushagrasinghx/BitChord).

Thanks also to the [contributors to BitChord](https://github.com/kushagrasinghx/BitChord/graphs/contributors).

### Credited by the Android project

- [binimum](https://github.com/binimum/am-lyrics) for the Apple-style lyrics animation, which the iOS lyrics view ports from Android. binimum also runs the BiniLyrics and LyricsPlus services the app reads lyrics from.

### Third-party code and models

[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) lists every third-party work in this repository or linked into the app, with its licence. In short:

- [AMSMB2](https://github.com/amosavian/AMSMB2), which wraps libsmb2 (LGPL-2.1), for SMB shares.
- [ONNX Runtime](https://github.com/microsoft/onnxruntime-swift-package-manager) (MIT) to run the Automix models.
- [Orchard](https://github.com/SFG5453/Orchard) by SFG545. The Automix analyzer and several Automix files are ported from Orchard through Myusic for Android and stay under AGPL-3.0.
- The Beat This! beat model by CPJKU and the Open-Unmix vocals model by Inria and SigSep.
- Stream resolution follows NewPipe Extractor, InnerTubeX and zemer-cipher; the Discord integration ports Kizzy; the artwork colours port AndroidX Palette and ColorUtils.

### Services

Lyrics come from LRCLIB, Musixmatch, Genius, KuGou, PaxSenix, BetterLyrics, BiniLyrics, LyricsPlus, SimpMusic, Unison, Megalobiz and YouTube Music. Animated covers come from Apple Music, Tidal, Spotify and a community canvas index. Listen Together uses the Myusic Listen Together backend from the Android project. Thanks to the people who run these services.

## Disclaimer and legal notice

Myusic for iOS is an independent, community-driven third-party audio player and client. It is not associated with Google LLC, YouTube, YouTube Music, Apple Inc. or any of their parent companies.

- **No media hosting.** Myusic does not host, upload or store copyrighted music. It plays files you import, files on your own network shares, and streams from public or user-authenticated APIs.
- **Fair use and API usage.** This software is made for personal research, education and fair use. You are responsible for making sure your use complies with your local copyright laws and the YouTube Terms of Service.
- **No guarantee of service.** Myusic does not guarantee that any third-party platform will keep working with it.
- **Copyleft.** Myusic is free software under GPL-3.0. Anyone may sell or redistribute copies, but every distribution must come with the corresponding source under the same license.

## License

Myusic for iOS is licensed under the [GNU General Public License v3.0](LICENSE). It is a port of Myusic for Android, which is GPL-3.0, so the port carries the same license. The files ported from Orchard remain under the [GNU Affero General Public License v3.0](LICENSES/AGPL-3.0.txt), as their headers state. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for the full list.

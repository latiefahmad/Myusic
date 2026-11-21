# Platform matrix

One product, three implementations, one contract. This file is the contract.

- **Kotlin** - Android phone, tablet, TV, Wear OS, and the JVM desktop
  (Windows, Linux, macOS).
- **Swift** - iPhone and iPad.
- **Go** - the Listen Together backend.
- **Shared fixtures** - InnerTube responses, lyrics formats, addon manifests,
  settings migrations. Every client's tests read the same JSON.

A feature is listed once and marked for each platform, so "why is this missing
on iOS?" has an answer in the table rather than in a discussion.

## Tiers

| Tier | Meaning |
|---|---|
| **1** | The product. Every platform either has it or has a platform-native equivalent. |
| **2** | Platform-specific. Present where the operating system makes it meaningful. |
| **3** | Opportunistic. May lag a release behind, or never arrive on a platform. |

## Tier 1 - the shared experience

| Feature | Android | Desktop (JVM) | iOS / iPadOS |
|---|---|---|---|
| Search, home, explore, library | Yes | In progress | Yes (fork baseline 1.8) |
| Playlists, albums, artists | Yes | In progress | Yes |
| Playback and queue | Yes | In progress | Yes |
| Lyrics (synced, translated) | Yes | In progress | Yes |
| Downloads and offline | Yes | In progress | Yes |
| Scrobbling (Last.fm, ListenBrainz) | Yes | In progress | Yes |
| Listen Together | Yes | In progress | Yes |
| Local music | Yes | In progress | Partial |
| Video playback | Yes | In progress | Not yet |
| Podcasts | Yes | In progress | Not yet |
| Top Picks, mood/genre | Yes | In progress | Not yet |
| Direct Source Stream | Yes | In progress | Not yet |
| Loop mix | Yes | In progress | Not yet |
| Player themes | Yes | In progress | Not yet |
| Content preferences | Yes | In progress | Not yet |
| Addon quality picker | Yes | In progress | Not yet |
| Offline device playlists | Yes | In progress | Not yet |

"In progress" means the module exists and is being brought up to the 1.0.0
feature set; it is not a promise for a particular release.

## Tier 2 - platform-only

| Feature | Android | Desktop | iOS / iPadOS |
|---|---|---|---|
| Android Auto | Yes | - | - |
| Android TV / Leanback | Yes (separate module) | - | - |
| Wear OS | Yes (separate module) | - | - |
| Picture-in-picture | Yes | Planned | Native PiP |
| Media session (Media3) | Yes | MPRIS (Linux), SMTC (Windows) | Now Playing |
| Tray / menu bar | - | Yes | - |
| Widgets | Yes | - | Yes |
| Share target | Yes | - | Yes |
| CarPlay | - | - | Entitlement required |
| Siri / App Intents | - | - | Entitlement required |
| Keyboard and pointer | Partial | Yes | iPadOS: in progress |
| Stage Manager / freeform window | - | Yes (desktop windows) | iPadOS |
| Tablet navigation rail | Yes (`sw600dp` and up) | - | iPad sidebar, in progress |

The tablet cut is the platform's own: the short edge of the window at
**600dp**, so a phone held sideways keeps the bottom bar. Above it the four
tabs stand in a rail down the leading edge and only the mini player sits at
the foot of the page, leaving the full height to the feed.

## Tier 3 - opportunistic

| Feature | Android | Desktop | iOS / iPadOS |
|---|---|---|---|
| Automix analysis | Yes (native) | Yes when CMake and a compiler are present | Not planned |
| USB DAC / bit-perfect | Yes | Platform mixer only | Platform mixer only |
| Discord Rich Presence | Yes | Yes | Not possible |
| Custom equalizer | Yes | Yes | Limited by AVAudioEngine |
| Local folders (SMB/WebDAV) | Yes | Partial | Partial |

## Distribution

| Platform | Channel |
|---|---|
| Android phone / tablet | GitHub Releases APK (`ZMyusic-<version>-android-phone-*.apk`) |
| Android TV | GitHub Releases APK (`ZMyusic-<version>-android-tv-*.apk`) |
| Wear OS | GitHub Releases APK (`ZMyusic-<version>-android-wear.apk`) |
| Windows | MSI / EXE / portable ZIP |
| Linux | DEB / RPM / AppImage |
| macOS | DMG, unsigned unless a Developer ID is configured |
| iPhone / iPad | AltStore, SideStore, or Ad Hoc with the user's own certificate |

No client is submitted to the Play Store or the App Store: both reject
third-party YouTube clients under their store policies, and the app is
GPL-3.0. Distribution is direct.

## Versioning

One version for every platform, from `build.gradle.kts`:
`zmyusicVersionCode` and `zmyusicVersionName`. A release tag is
`ZMyusic-v<version>`, and every workflow stamps that version into the files it
builds, so one release page carries every platform at the same version.

CI checks the pair before it builds a tag: the tag must equal
`zmyusicVersionName`, and `zmyusicVersionCode` must be higher than the last
published release's APK. A tag that disagrees with the code, or that would
move "latest" backwards, fails instead of shipping an update no client can
install.

# Third-party notices

ZMyusic for iOS is licensed under the [GNU General Public License v3.0](LICENSE). This file lists the third-party works that the repository contains, that the app links, or whose code or design the Swift code ports. For each one it gives the licence and where the work is used.

A licence is given only where a licence file or a licence statement was found. Where none was found, the entry says "licence not confirmed".

## ZMyusic for Android

- Project: [ZMyusic](https://github.com/latiefahmad/ZMyusic), a rebrand of [BitChord](https://github.com/kushagrasinghx/BitChord) by Kushagra Singh.
- Licence: GPL-3.0 (the upstream `LICENSE` file).
- Used in: the whole app. Most Swift files name the Android file they port in their header, with paths relative to `app/src/main/java/com/zmyusic/zmyusic/` in the Android repository. Files that carry a licence header name Kushagra Singh as the copyright holder of the original work.

## Code in this repository

### Orchard

- Project: [Orchard](https://github.com/SFG5453/Orchard) by SFG545, ported to ZMyusic for Android and from there to iOS.
- Licence: AGPL-3.0-or-later, as stated in each file's header. The full text is in [LICENSES/AGPL-3.0.txt](LICENSES/AGPL-3.0.txt). The headers state that these files are combined into ZMyusic, a GPL-3.0-or-later work, under section 13 of the AGPL-3.0, and that each file remains governed by the AGPL-3.0.
- Files: every file whose header says "Orchard's original source is licensed under the GNU Affero General Public License". There are 17:
  - `ZMyusicKit/Sources/AutomixAnalyzer/` (all 11 files): `automix_analyzer_bridge.cpp`, `include/AutomixAnalyzer.h`, and `analyzer/audio_analysis.cpp`, `audio_analysis.h`, `mel_spectrogram.cpp`, `mel_spectrogram.h`, `resampler.cpp`, `resampler.h`, `tempo_analysis.cpp`, `vocal_spectrogram.cpp`, `vocal_spectrogram.h`.
  - `ZMyusicKit/Sources/Automix/`: `BeatTracker.swift`, `NativeAnalyzer.swift`, `TrackAnalysis.swift`, `TransitionPlanner.swift`, `TransitionPolicy.swift`, `VocalTracker.swift`.
- Also credited: `AutomixAudioDecoder.swift` and `TrackAnalyzer.swift` in `ZMyusicKit/Sources/Automix/` say they are modelled on Orchard's `AudioDecoder` and `TrackAnalyzer`. Their headers license them under GPL-3.0-or-later.

### Beat This! front end

- Projects: [Beat This!](https://github.com/CPJKU/beat_this) by CPJKU, and [beat_this_cpp](https://github.com/mosynthkey/beat_this_cpp) by mosynthkey.
- Licence: MIT for both, as stated in the comment in `mel_spectrogram.h`. Not checked against the projects' own licence files.
- Used in: `ZMyusicKit/Sources/AutomixAnalyzer/analyzer/mel_spectrogram.{h,cpp}`, whose log-mel front end follows `LogMelSpect` from Beat This! and its C++ port.

### Open-Unmix front end

- Project: [Open-Unmix](https://github.com/sigsep/open-unmix-pytorch) by Inria and SigSep.
- Licence: MIT, as stated in the comment in `vocal_spectrogram.h` (for `openunmix/transforms.py`). Not checked against the project's own licence file.
- Used in: `ZMyusicKit/Sources/AutomixAnalyzer/analyzer/vocal_spectrogram.{h,cpp}`, whose STFT front end follows Open-Unmix's `TorchSTFT`.

## Models in this repository

Both models are byte-identical to the copies in ZMyusic for Android (`app/src/main/assets/`). They are loaded by `ZMyusicKit/Sources/Automix/AutomixModelSession.swift`.

| File | Model | Origin | Licence |
|---|---|---|---|
| `ZMyusicKit/Sources/Automix/Models/beat_this_int8.onnx` | Beat This! beat and downbeat tracker, int8 | CPJKU ([beat_this](https://github.com/CPJKU/beat_this)) | MIT for code and weights, as stated in `AutomixModelSession.swift` and `BeatTracker.swift`. Not checked against the release. |
| `ZMyusicKit/Sources/Automix/Models/vocals_umxhq_int8.onnx` | Open-Unmix UMX-HQ "vocals" target, int8 | Inria and SigSep ([open-unmix-pytorch](https://github.com/sigsep/open-unmix-pytorch)) | MIT weights, as stated in `AutomixModelSession.swift`. The Android source says this was confirmed on the Zenodo deposit. Not checked against the deposit. |

Who converted the models to int8 ONNX is not recorded in either repository.

## Swift package dependencies

Resolved versions are pinned in `ZMyusicKit/Package.resolved`.

### AMSMB2

- Project: [AMSMB2](https://github.com/amosavian/AMSMB2) 4.0.3 by amosavian.
- Licence: the package's `LICENSE` file is LGPL-2.1. Its own Swift sources say they are MIT, and its README explains that the package as a whole is LGPL-2.1 because it statically links libsmb2.
- Used in: `NetworkLibrary`, for SMB shares.

### libsmb2

- Project: libsmb2 by Ronnie Sahlberg, bundled inside AMSMB2 (`Dependencies/libsmb2`).
- Licence: LGPL-2.1-or-later for the library (`lib` and `include`), per its `COPYING` file. Its `examples` directory is BSD-2-Clause and is not used.
- Used in: through AMSMB2.

The LGPL-2.1 lets you replace these libraries with a modified version. The full source of this app is in this repository, so you can rebuild it against a modified AMSMB2 or libsmb2 by changing the package dependency in `ZMyusicKit/Package.swift`.

### ONNX Runtime

- Project: [onnxruntime-swift-package-manager](https://github.com/microsoft/onnxruntime-swift-package-manager) 1.24.2 by Microsoft, which downloads the prebuilt ONNX Runtime C library (`pod-archive-onnxruntime-c-1.24.2.zip`).
- Licence: MIT (the package's `LICENSE` file and the `LICENSE` file inside the binary archive).
- Used in: `Automix`, to run the two models above.

## Code whose logic is ported or followed

No verbatim source from these projects was found in this repository. The Swift code reimplements their behaviour, usually through the Android app's use of them.

| Project | Licence | Where | Relationship |
|---|---|---|---|
| [NewPipe Extractor](https://github.com/TeamNewPipe/NewPipeExtractor) by TeamNewPipe | GPL-3.0-or-later, as stated in the file ZMyusic for Android vendors from it (`org/schabi/newpipe/extractor/utils/Utils.java`, from v0.26.3) | `ZMyusicKit/Sources/StreamResolution/` (`StreamCipherSolver.swift`, `StreamClientProfile.swift`, `StreamPlayerClient.swift`, `InnerTubeStreamExtractor.swift`, `PlayerResponse.swift`) | Client requests, user agents and the signature and `n` solving follow NewPipe. |
| [InnerTubeX](https://github.com/MetrolistGroup/innertubex) by MetrolistGroup | GPL-3.0 | `ZMyusicKit/Sources/StreamResolution/` (`InnerTubeStreamExtractor.swift` ports `InnerTubeXResolver`; `StreamClientProfile.swift`, `StreamPlayerClient.swift`, `StreamURLProbe.swift`), `ZMyusicKit/Sources/AudioCache/HTTPAudioSource.swift` | The client catalogue and range limits follow InnerTubeX, which the Android app uses (v0.7.0). |
| [zemer-cipher](https://github.com/ZemerTeam/zemer-cipher) by ZemerTeam | GPL-3.0, as stated in the comment in `PlayerScriptConfig.swift` | `ZMyusicKit/Sources/StreamResolution/Cipher/` (`PlayerScriptConfig.swift`, `StreamCipherSolver.swift`, `PlayerScriptRuntime.swift`) | The config model is a port of zemer-cipher's. At run time the app downloads zemer-cipher's `player_configs.json` from its GitHub repository. |
| [Kizzy](https://github.com/dead8309/Kizzy) by yzziK (Vaibhav), vendored in ZMyusic for Android under `com/my/kizzy` | GPL-3.0, as published in the Kizzy repository | `ZMyusicKit/Sources/Integrations/` (`DiscordGatewaySocket.swift`, `DiscordGatewayPayloads.swift`, `DiscordAccountService.swift`) | The Discord gateway client ports Kizzy's RPC code. |
| AndroidX Core `ColorUtils` (Android Open Source Project) | Apache-2.0 | `ZMyusicKit/Sources/Theming/ColorUtilsPort.swift` | A line-for-line port of the colour functions the Android code uses. |
| AndroidX Palette (Android Open Source Project) | Apache-2.0 | `ZMyusicKit/Sources/Theming/ColorCutQuantizer.swift`, `SwatchPalette.swift` | Ports of `ColorCutQuantizer`, `Palette.Swatch`, `Target` and `Palette.Filter`. |
| [am-lyrics](https://github.com/binimum/am-lyrics) by binimum | MPL-2.0 | `App/ZMyusic/Features/Lyrics/` | The Android project credits am-lyrics for its Apple-style lyrics animation, which the iOS lyrics view ports from Android. |

## Other bundled content

- BotGuard client page: `ZMyusicKit/Sources/StreamResolution/PoToken/PoTokenPage.swift` holds the page ZMyusic for Android ships as `app/src/main/assets/po_token.html`. Neither copy states an origin or a licence. Licence not confirmed.
- Test fixtures: the `Fixtures/` folders under `ZMyusicKit/Tests/` and `App/ZMyusicTests/` hold responses recorded from the services the app talks to, for offline tests. They include a compressed copy of YouTube's player script (`ZMyusicKit/Tests/StreamResolutionTests/Fixtures/player_ias_*.js.deflate`), lyrics provider responses that contain song lyrics (`ZMyusicKit/Tests/LyricsTests/Fixtures/`), two album cover images (`ZMyusicKit/Tests/ThemingTests/Fixtures/*.jpg`) and YouTube Music page and API responses. These remain the property of their owners and are not covered by this repository's licence.

# Security policy

## Reporting a vulnerability

Email **pingwave.id@gmail.com** with what you found and how to reproduce it.
Please do not open a public issue for anything exploitable. You get an
acknowledgement within a few days.

## Secrets in this repository

GitHub's secret scanning flags four `AIza…` values under
`ios/MyusicKit`. They are **not** credentials of this project and there is
nothing to rotate:

- `ios/MyusicKit/Tests/**/Fixtures/*` are recorded YouTube and Musixmatch
  responses. The `AIza…` strings in them are the public client keys those web
  pages ship with — `INNERTUBE_API_KEY` in a saved `music.youtube.com` page, and
  the key in Musixmatch's own app config. The Musixmatch `user_token` in the
  same fixture is literally `REDACTED` upstream.
- `ios/MyusicKit/Sources/StreamResolution/PoToken/PoTokenChallenge.swift` and
  `app/src/main/java/com/music/myusic/data/innertube/potoken/PoTokenWebView.kt`
  hold YouTube's public BotGuard key, the one every third-party YouTube client
  uses to mint po-tokens. It has to be in the source to speak to YouTube's
  `api/jnn` endpoints.

All of these were already public in the upstream BitChord repository and in
youtube.com itself. `.github/secret_scanning.yml` excludes exactly those paths,
so any real secret committed anywhere else is still reported.

## Supported versions

The latest release is supported. This is a one-person project: fixes land on
`main` and ship in the next build.

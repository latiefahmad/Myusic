# onnxruntime-swift-package-manager (vendored)

The ZMyusic iOS port links ONNX Runtime through the official Swift package, which
`ZMyusicKit/Package.swift` used to fetch from
`https://github.com/microsoft/onnxruntime-swift-package-manager`.

Microsoft removed that repository around 2026-11-17, so a clean checkout can no
longer resolve it (`fatal: could not read Username for 'https://github.com'`).
This directory is that package, unmodified:

- Upstream: `microsoft/onnxruntime-swift-package-manager`
- Version: 1.24.2
- Commit: `b7fb7f7dea8a2469e6335d95a61b8f36d0dc83b2` — the exact revision
  `ZMyusicKit/Package.resolved` had already pinned, so the git object hash
  guarantees this copy is byte-for-byte the tree the project was built against.
- License: MIT, see `LICENSE`.
- Retrieved from a public mirror of that commit after the upstream deletion.

Nothing here is patched. `Package.swift` still points `onnxruntime` and
`onnxruntime_extensions` at Microsoft's own release archives on
`download.onnxruntime.ai`, with the SHA-256 checksums Microsoft published in the
same commit, so the compiled binaries keep their original provenance.

When Microsoft restores the repository, switch `ZMyusicKit/Package.swift` back to
`.package(url: "https://github.com/microsoft/onnxruntime-swift-package-manager",
exact: "1.24.2")` and delete this directory.

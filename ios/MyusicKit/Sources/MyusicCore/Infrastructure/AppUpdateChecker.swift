import Foundation

// Ports data/AppUpdateChecker.kt. The app is sideloaded - AltStore, SideStore or an Ad Hoc
// profile - so no store pushes an update notice; this reads the repo's "latest release" and says
// whether a newer build is out. It only ever *tells* the listener: the iOS build has no way to
// install itself, so the row opens the release page in Safari and the update is applied the way
// the app was first installed.

/// What one ``AppUpdateChecker/check(force:)`` found.
public enum AppUpdateCheckResult: Equatable, Sendable {
    /// A newer release is out; ``AppUpdateChecker/available`` carries its version and page.
    case updateAvailable
    /// The running build is the newest one /releases/latest serves.
    case upToDate
    /// GitHub could not be reached, or answered with something unparseable.
    case failed
    /// A check ran recently enough that this one was skipped; see ``AppUpdateChecker/interval``.
    case skipped
}

/// Polls `latiefahmad/Myusic`'s latest release. The shape mirrors the Android checker: an
/// ``available`` value the UI observes, an explicit result for a row that asks on demand, and a
/// throttle so a resume does not hit GitHub every time.
public final class AppUpdateChecker {

    /// One release worth offering.
    public struct UpdateInfo: Equatable, Sendable {
        /// The version the tag names, without the `Myusic-v` stem: "1.0.0".
        public let version: String
        /// The release page, opened in Safari to install.
        public let releaseUrl: URL
        /// The release's own Markdown body, shown as this update's "what's new", or nil.
        public let notes: String?
    }

    public static let shared = AppUpdateChecker()

    /// How long a check stands before the next one asks GitHub again. A cold start always checks
    /// (the process's first call is never throttled); this only keeps a quick switch away and back
    /// from repeating the request.
    public static let interval: TimeInterval = 6 * 60 * 60

    private static let latestReleaseURL =
        URL(string: "https://api.github.com/repos/latiefahmad/Myusic/releases/latest")!

    private let session: URLSession
    private let currentVersion: () -> String?
    private let now: () -> Date

    private let lock = NSLock()
    private var lastCheckAt: Date?
    private var availableValue: UpdateInfo?

    /// The newest release found, cleared when a check no longer sees one. Read by the UI.
    public var available: UpdateInfo? {
        lock.lock(); defer { lock.unlock() }
        return availableValue
    }

    /// `session` defaults to ``MyusicHTTP/session``; tests pass a stub. `currentVersion` defaults to
    /// the main bundle's `CFBundleShortVersionString`, so a test can pin the running build.
    public init(session: URLSession = MyusicHTTP.session,
                currentVersion: @escaping () -> String? = AppUpdateChecker.bundleVersion,
                now: @escaping () -> Date = Date.init) {
        self.session = session
        self.currentVersion = currentVersion
        self.now = now
    }

    static func bundleVersion() -> String? {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String
    }

    /// Polls the latest release. `force` skips the interval, for a row the listener tapped.
    ///
    /// Network and parse failures are reported rather than thrown, so a caller can tell "up to
    /// date" from "couldn't ask".
    @discardableResult
    public func check(force: Bool = false) async -> AppUpdateCheckResult {
        let instant = now()
        lock.lock()
        if !force, let last = lastCheckAt, instant.timeIntervalSince(last) < Self.interval {
            lock.unlock()
            return .skipped
        }
        lastCheckAt = instant
        lock.unlock()

        var request = URLRequest(url: Self.latestReleaseURL)
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        request.setValue(MyusicHTTP.UserAgent.app, forHTTPHeaderField: "User-Agent")
        request.setValue("Myusic/\(currentVersion() ?? "0")", forHTTPHeaderField: "X-Myusic-Version")

        let outcome: AppUpdateCheckResult
        var found: UpdateInfo?
        do {
            let (data, response) = try await session.data(for: request)
            outcome = Self.parse(data: data,
                                 status: (response as? HTTPURLResponse)?.statusCode,
                                 currentVersion: currentVersion(),
                                 into: &found)
        } catch {
            outcome = .failed
        }

        lock.lock()
        // A release can be edited or pulled; don't keep offering one this check no longer sees.
        availableValue = found
        lock.unlock()
        return outcome
    }

    /// Reads a `releases/latest` body. Split out because it is the only part that can be tested
    /// without a network round trip; `found` is set when the answer is a newer release.
    static func parse(data: Data, status: Int?, currentVersion: String?,
                      into found: inout UpdateInfo?) -> AppUpdateCheckResult {
        guard status == 200,
              let release = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let tag = release["tag_name"] as? String,
              let urlString = release["html_url"] as? String,
              let url = URL(string: urlString) else {
            return .failed
        }
        // Releases made before the tag took the app's name were plain "v1.9.1", so both stems strip.
        let latest = tag.hasPrefix("Myusic-v") ? String(tag.dropFirst("Myusic-v".count))
            : tag.hasPrefix("v") ? String(tag.dropFirst()) : tag
        guard isNewer(latest, currentVersion) else { return .upToDate }
        found = UpdateInfo(version: latest, releaseUrl: url, notes: release["body"] as? String)
        return .updateAvailable
    }

    /// Numeric, component by component, so 1.10.0 beats 1.9.0 (a plain string compare does not).
    /// A `-beta` suffix on either side is ignored: the digits decide.
    static func isNewer(_ candidate: String, _ running: String?) -> Bool {
        guard let running else { return false }
        func parts(_ value: String) -> [Int] {
            value.split(separator: ".").map { Int($0.prefix(while: \.isNumber)) ?? 0 }
        }
        let a = parts(candidate), b = parts(running)
        for i in 0..<max(a.count, b.count) {
            let x = i < a.count ? a[i] : 0
            let y = i < b.count ? b[i] : 0
            if x != y { return x > y }
        }
        return false
    }
}

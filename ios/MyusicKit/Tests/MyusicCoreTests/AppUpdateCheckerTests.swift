import XCTest
import MyusicTestSupport
@testable import MyusicCore

/// The update checker talks to GitHub's `releases/latest`; these pin the version comparison, the
/// release-body parsing and the six-hour throttle, all without a network.
final class AppUpdateCheckerTests: XCTestCase {

    /// A `releases/latest` body. `tag` defaults to the current `Myusic-v<version>` convention but
    /// can be overridden to exercise the older plain-`v` tags.
    private func releaseJSON(version: String,
                             tag: String? = nil,
                             url: String = "https://github.com/latiefahmad/Myusic/releases/tag/Myusic-v1.2.0",
                             notes: String = "What's new") -> String {
        let tagName = tag ?? "Myusic-v\(version)"
        return """
        {"tag_name": "\(tagName)", "html_url": "\(url)", "body": "\(notes)"}
        """
    }

    // MARK: Version compare

    func testANewerReleaseIsNewer() {
        XCTAssertTrue(AppUpdateChecker.isNewer("1.2.0", "1.1.9"))
        XCTAssertTrue(AppUpdateChecker.isNewer("2.0.0", "1.99.99"))
        // The one a string compare gets wrong.
        XCTAssertTrue(AppUpdateChecker.isNewer("1.10.0", "1.9.0"))
        XCTAssertFalse(AppUpdateChecker.isNewer("1.9.0", "1.10.0"))
    }

    func testTheSameVersionIsNotNewer() {
        XCTAssertFalse(AppUpdateChecker.isNewer("1.0.0", "1.0.0"))
        XCTAssertFalse(AppUpdateChecker.isNewer("1.0", "1.0.0"))
    }

    func testAPreReleaseSuffixIsIgnored() {
        XCTAssertFalse(AppUpdateChecker.isNewer("1.0.0-beta1", "1.0.0"))
        XCTAssertTrue(AppUpdateChecker.isNewer("1.1.0-beta1", "1.0.0"))
    }

    func testAMissingRunningVersionIsNeverNewer() {
        XCTAssertFalse(AppUpdateChecker.isNewer("9.9.9", nil))
    }

    // MARK: Parsing

    func testAPublishedReleaseIsOffered() {
        var found: AppUpdateChecker.UpdateInfo?
        let result = AppUpdateChecker.parse(data: Data(releaseJSON(version: "1.2.0").utf8),
                                            status: 200, currentVersion: "1.0.0", into: &found)
        XCTAssertEqual(result, .updateAvailable)
        XCTAssertEqual(found?.version, "1.2.0")
        XCTAssertEqual(found?.notes, "What's new")
        XCTAssertEqual(found?.releaseUrl.absoluteString,
                       "https://github.com/latiefahmad/Myusic/releases/tag/Myusic-v1.2.0")
    }

    func testTheRunningsVersionIsUpToDate() {
        var found: AppUpdateChecker.UpdateInfo?
        let result = AppUpdateChecker.parse(data: Data(releaseJSON(version: "1.0.0").utf8),
                                            status: 200, currentVersion: "1.0.0", into: &found)
        XCTAssertEqual(result, .upToDate)
        XCTAssertNil(found)
    }

    func testALegacyTagWithNoAppStemStillParses() {
        var found: AppUpdateChecker.UpdateInfo?
        let result = AppUpdateChecker.parse(data: Data(releaseJSON(version: "1.10.0", tag: "v1.10.0").utf8),
                                            status: 200, currentVersion: "1.9.0", into: &found)
        XCTAssertEqual(result, .updateAvailable)
        XCTAssertEqual(found?.version, "1.10.0")
    }

    func testUnparseableOrFailedAnswersReportFailure() {
        var found: AppUpdateChecker.UpdateInfo?
        XCTAssertEqual(AppUpdateChecker.parse(data: Data("{not json".utf8), status: 200,
                                              currentVersion: "1.0.0", into: &found), .failed)
        XCTAssertEqual(AppUpdateChecker.parse(data: Data(#"{"tag_name":"Myusic-v1.2.0"}"#.utf8), status: 200,
                                              currentVersion: "1.0.0", into: &found), .failed,
                       "no html_url")
        XCTAssertEqual(AppUpdateChecker.parse(data: Data(releaseJSON(version: "1.2.0").utf8), status: 404,
                                              currentVersion: "1.0.0", into: &found), .failed)
    }

    // MARK: Network + throttle

    func testChecksTheLatestReleaseOverTheInjectedSession() async {
        let stub = URLProtocolStub()
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .json(releaseJSON(version: "1.2.0")))
        let checker = AppUpdateChecker(session: stub.makeSession(), currentVersion: { "1.0.0" })

        // Awaited into a plain value first: XCTAssert* take autoclosures, which cannot hold `await`.
        let result = await checker.check()
        XCTAssertEqual(result, .updateAvailable)
        XCTAssertEqual(checker.available?.version, "1.2.0")
        XCTAssertEqual(stub.requests.count, 1)
        XCTAssertEqual(stub.requests.first?.value(forHTTPHeaderField: "Accept"), "application/vnd.github+json")
    }

    func testASecondCheckInsideTheWindowIsSkipped() async {
        let stub = URLProtocolStub()
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .json(releaseJSON(version: "1.2.0")))
        // A box, not a captured `var`: the checker holds the closure and the test keeps moving the
        // clock, and a captured mutable local under strict concurrency is a warning at best.
        final class Clock { var now = Date(timeIntervalSince1970: 1_700_000_000) }
        let clock = Clock()
        let checker = AppUpdateChecker(session: stub.makeSession(), currentVersion: { "1.0.0" },
                                       now: { clock.now })

        let first = await checker.check()
        XCTAssertEqual(first, .updateAvailable)
        clock.now = clock.now.addingTimeInterval(AppUpdateChecker.interval - 60)
        let throttled = await checker.check()
        XCTAssertEqual(throttled, .skipped, "inside the window")
        XCTAssertEqual(stub.requests.count, 1, "the throttled check made no request")

        clock.now = clock.now.addingTimeInterval(120)
        let afterWindow = await checker.check()
        XCTAssertEqual(afterWindow, .updateAvailable, "past the window")
        XCTAssertEqual(stub.requests.count, 2)
    }

    func testAForcedCheckIgnoresTheThrottle() async {
        let stub = URLProtocolStub()
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .json(releaseJSON(version: "1.2.0")))
        let checker = AppUpdateChecker(session: stub.makeSession(), currentVersion: { "1.0.0" })

        _ = await checker.check()
        let forced = await checker.check(force: true)
        XCTAssertEqual(forced, .updateAvailable)
        XCTAssertEqual(stub.requests.count, 2)
    }

    func testAPulledReleaseStopsBeingOffered() async {
        let stub = URLProtocolStub()
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .json(releaseJSON(version: "1.2.0")))
        let checker = AppUpdateChecker(session: stub.makeSession(), currentVersion: { "1.0.0" })
        let offered = await checker.check()
        XCTAssertEqual(offered, .updateAvailable)
        XCTAssertNotNil(checker.available)

        // The release was edited down to the running version.
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .json(releaseJSON(version: "1.0.0")))
        let pulled = await checker.check(force: true)
        XCTAssertEqual(pulled, .upToDate)
        XCTAssertNil(checker.available, "a release no longer seen must not keep being offered")
    }

    func testATransportFailureReportsFailure() async {
        let stub = URLProtocolStub()
        stub.register(host: "api.github.com", path: "/repos/latiefahmad/Myusic/releases/latest",
                      response: .failure(.notConnectedToInternet))
        let checker = AppUpdateChecker(session: stub.makeSession(), currentVersion: { "1.0.0" })
        let result = await checker.check()
        XCTAssertEqual(result, .failed)
        XCTAssertNil(checker.available)
    }
}

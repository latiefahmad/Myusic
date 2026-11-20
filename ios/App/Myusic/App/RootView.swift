import MyusicCore
import SwiftUI

/// The window's root: builds the app once and hands it to every view through the environment.
///
/// In the unit-test host no app is built (tests construct what they exercise), so a test run
/// never starts the engine, restores a queue or talks to the network.
struct RootView: View {
    // `AppModel.current` first: a widget button, Siri or CarPlay may have started the app in the
    // background before any window existed (SystemAppAccess), and there must be one app, not two.
    @State private var model: AppModel? = RootView.isUnitTestHost ? nil : (AppModel.current ?? AppModel.live())

    /// XCTest injects its configuration into the host app's environment; UI tests don't (their
    /// runner is a separate process), so they get the real app.
    static var isUnitTestHost: Bool {
        ProcessInfo.processInfo.environment["XCTestConfigurationFilePath"] != nil
    }

    var body: some View {
        if let model {
            AppShell(model: model)
        } else {
            Color(.systemBackground)
        }
    }
}

/// The running app: the tab shell with every environment value it reads, the theme and language,
/// deep links, and the scene lifecycle.
struct AppShell: View {
    let model: AppModel
    @Environment(\.scenePhase) private var scenePhase
    /// The update the listener has already answered, so the launch notice shows once and the
    /// settings row underneath stays quiet about the same version.
    @State private var acknowledgedUpdate: String?

    var body: some View {
        RootTabView()
            .id(model.languageRevision)
            .environment(model)
            .environment(model.router)
            .environment(model.player)
            .environment(model.settings)
            .environment(model.likeState)
            .environment(model.searchHistory)
            // Theme.kt: System follows the device; Light and Dark force it on every screen,
            // presented sheets included.
            .preferredColorScheme(model.settings.themeMode.colorScheme)
            // The in-app language (LanguageBundle): number formats and right-to-left mirroring.
            .environment(\.locale, LanguageBundle.locale)
            .environment(\.layoutDirection, LanguageBundle.layoutDirection)
            // Sideloaded, so nothing else says a new build is out: one alert per version per
            // launch. "Later" only closes it; the Settings row can always ask again.
            .alert(updateAlertVersion.map { L10n.updateAvailable($0) } ?? L10n.softwareUpdate,
                   isPresented: updateAlertShown) {
                Button(L10n.download) { openUpdatePage() }
                Button(L10n.later, role: .cancel) { acknowledgedUpdate = model.availableUpdate?.version }
            } message: {
                if let update = model.availableUpdate {
                    Text(updateMessage(for: update))
                }
            }
            .onOpenURL { url in model.open(url) }
            .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
                if let url = activity.webpageURL { model.open(url) }
            }
            .onChange(of: scenePhase) { _, phase in
                model.scenePhaseChanged(phase)
            }
            .task { model.start() }
    }

    private var updateAlertVersion: String? {
        guard let update = model.availableUpdate, update.version != acknowledgedUpdate else { return nil }
        return update.version
    }

    private var updateAlertShown: Binding<Bool> {
        Binding(get: { updateAlertVersion != nil },
                set: { if !$0 { acknowledgedUpdate = model.availableUpdate?.version } })
    }

    private func openUpdatePage() {
        if let url = model.availableUpdate?.releaseUrl { UIApplication.shared.open(url) }
        acknowledgedUpdate = model.availableUpdate?.version
    }

    private func updateMessage(for update: AppUpdateChecker.UpdateInfo) -> String {
        let body = L10n.updateAvailableBody(update.version)
        guard let notes = update.notes, !notes.isEmpty else { return body }
        return "\(body)\n\n\(notes.prefix(600))"
    }
}

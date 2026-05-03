import Foundation
import UIKit

enum ShortcutLauncher {
    /// Run the shortcut, passing current config as JSON input so the manual
    /// "Run Now" reflects edits even before iCloud Drive has synced.
    @MainActor
    static func runNow(config: OnTimeConfig) {
        let json = (try? JSONEncoder().encode(config)).flatMap { String(data: $0, encoding: .utf8) } ?? "{}"
        var components = URLComponents()
        components.scheme = "shortcuts"
        components.host = "run-shortcut"
        components.queryItems = [
            URLQueryItem(name: "name", value: AppConstants.shortcutName),
            URLQueryItem(name: "input", value: "text"),
            URLQueryItem(name: "text", value: json),
        ]
        guard let url = components.url else { return }
        UIApplication.shared.open(url)
    }

    @MainActor
    static func openShortcutsApp() {
        if let url = URL(string: "shortcuts://") {
            UIApplication.shared.open(url)
        }
    }

    @MainActor
    static func openInstallURL() {
        if let url = URL(string: AppConstants.shortcutInstallURL) {
            UIApplication.shared.open(url)
        }
    }
}

import Foundation

/// Persists `OnTimeConfig` to UserDefaults. The companion Shortcut receives
/// the config via URL-scheme input on every "Run Now"; the daily automation
/// uses the defaults baked into the shortcut itself.
@MainActor
final class ConfigStore: ObservableObject {
    @Published private(set) var config: OnTimeConfig

    private let key = "OnTimeConfig.v1"
    private let defaults = UserDefaults.standard

    init() {
        if let data = UserDefaults.standard.data(forKey: "OnTimeConfig.v1"),
           let decoded = try? JSONDecoder().decode(OnTimeConfig.self, from: data) {
            self.config = decoded
        } else {
            self.config = .default
        }
    }

    func update(_ mutate: (inout OnTimeConfig) -> Void) {
        var next = config
        mutate(&next)
        guard next != config else { return }
        config = next
        if let data = try? JSONEncoder().encode(config) {
            defaults.set(data, forKey: key)
        }
    }
}

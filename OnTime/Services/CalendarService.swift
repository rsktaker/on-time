import EventKit
import Foundation

@MainActor
final class CalendarService: ObservableObject {
    @Published var calendars: [EKCalendar] = []
    @Published var authorizationStatus: EKAuthorizationStatus = EKEventStore.authorizationStatus(for: .event)

    private let store = EKEventStore()

    func requestAccess() async {
        do {
            if #available(iOS 17.0, *) {
                _ = try await store.requestFullAccessToEvents()
            } else {
                _ = try await store.requestAccess(to: .event)
            }
        } catch {
            // User-denied or restricted; reflected in authorizationStatus below.
        }
        authorizationStatus = EKEventStore.authorizationStatus(for: .event)
        await reload()
    }

    func reload() async {
        guard authorizationStatus == .authorized || authorizationStatus == .fullAccess else {
            calendars = []
            return
        }
        let all = store.calendars(for: .event)
            .filter { $0.allowsContentModifications || $0.type != .subscription || true }
            .sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
        calendars = all
    }
}

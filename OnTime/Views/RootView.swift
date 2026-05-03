import EventKit
import SwiftUI

struct RootView: View {
    @StateObject private var store = ConfigStore()
    @StateObject private var calendars = CalendarService()
    @State private var showContact = false
    @State private var showAutomation = false

    var body: some View {
        NavigationStack {
            List {
                bufferSection
                calendarsSection
                runSection
                setupSection
                aboutSection
            }
            .listStyle(.insetGrouped)
            .navigationTitle("On Time")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showContact) { ContactView() }
            .sheet(isPresented: $showAutomation) { AutomationGuideView() }
            .task {
                if calendars.authorizationStatus == .notDetermined {
                    await calendars.requestAccess()
                } else {
                    await calendars.reload()
                }
            }
        }
    }

    private var bufferSection: some View {
        Section {
            Stepper(value: Binding(
                get: { store.config.bufferMinutes },
                set: { v in store.update { $0.bufferMinutes = v } }
            ), in: AppConstants.minBufferMinutes...AppConstants.maxBufferMinutes) {
                HStack {
                    Text("Buffer")
                    Spacer()
                    Text("\(store.config.bufferMinutes) min")
                        .foregroundStyle(.secondary)
                        .monospacedDigit()
                }
            }
        } header: {
            Text("Alarm Timing")
        } footer: {
            Text("Alarms ring this many minutes before each calendar event starts.")
        }
    }

    @ViewBuilder
    private var calendarsSection: some View {
        Section {
            switch calendars.authorizationStatus {
            case .notDetermined:
                Button("Grant Calendar Access") {
                    Task { await calendars.requestAccess() }
                }
            case .denied, .restricted:
                VStack(alignment: .leading, spacing: 6) {
                    Text("Calendar access is off.")
                    Text("Open Settings → On Time → Calendars to enable.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            default:
                if calendars.calendars.isEmpty {
                    Text("No calendars found.").foregroundStyle(.secondary)
                } else {
                    ForEach(calendars.calendars, id: \.calendarIdentifier) { cal in
                        Toggle(isOn: binding(for: cal)) {
                            HStack(spacing: 10) {
                                Circle()
                                    .fill(Color(cgColor: cal.cgColor))
                                    .frame(width: 10, height: 10)
                                Text(cal.title)
                            }
                        }
                    }
                }
            }
        } header: {
            Text("Calendars")
        } footer: {
            Text("Toggled-off calendars won't trigger alarms. Tip: turn off calendars like \u{201C}Know, Don't Go\u{201D}.")
        }
    }

    private var runSection: some View {
        Section {
            Button {
                ShortcutLauncher.runNow(config: store.config)
            } label: {
                Label("Run Now", systemImage: "play.fill")
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.vertical, 4)
                    .font(.headline)
            }
            .buttonStyle(.borderedProminent)
            .listRowInsets(EdgeInsets(top: 12, leading: 16, bottom: 12, trailing: 16))
            .listRowBackground(Color.clear)
        } footer: {
            Text("Recreates today's alarms with current settings. Requires the On Time shortcut to be installed.")
        }
    }

    private var setupSection: some View {
        Section {
            Button {
                ShortcutLauncher.openInstallURL()
            } label: {
                Label("Install Shortcut", systemImage: "square.and.arrow.down")
            }
            Button {
                showAutomation = true
            } label: {
                Label("Set Up Daily Automation", systemImage: "clock.arrow.circlepath")
            }
        } header: {
            Text("Setup")
        } footer: {
            Text("Install once, then add a 12:01 AM personal automation in Shortcuts so alarms refresh nightly.")
        }
    }

    private var aboutSection: some View {
        Section {
            Button("Contact") { showContact = true }
            Link("View on GitHub", destination: URL(string: AppConstants.supportURL)!)
        } footer: {
            Text("On Time \(Bundle.main.appVersion) · Made by Ruchir Kavulli")
                .frame(maxWidth: .infinity, alignment: .center)
        }
    }

    private func binding(for cal: EKCalendar) -> Binding<Bool> {
        Binding(
            get: { !store.config.excludedCalendarTitles.contains(cal.title) },
            set: { isOn in
                store.update { cfg in
                    var set = Set(cfg.excludedCalendarTitles)
                    if isOn { set.remove(cal.title) } else { set.insert(cal.title) }
                    cfg.excludedCalendarTitles = Array(set).sorted()
                }
            }
        )
    }
}

private extension Bundle {
    var appVersion: String {
        let v = infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
        let b = infoDictionary?["CFBundleVersion"] as? String ?? "1"
        return "v\(v) (\(b))"
    }
}

import SwiftUI

struct AutomationGuideView: View {
    @Environment(\.dismiss) private var dismiss

    private let steps: [(String, String)] = [
        ("1", "Open the Shortcuts app."),
        ("2", "Tap Automation, then the + in the top right."),
        ("3", "Choose Time of Day. Set 12:01 AM, Daily."),
        ("4", "Turn off Run After Confirmation."),
        ("5", "Tap Next, then choose the On Time shortcut."),
        ("6", "Tap Done. You're set — alarms refresh nightly."),
    ]

    var body: some View {
        NavigationStack {
            List {
                Section {
                    ForEach(steps, id: \.0) { num, text in
                        HStack(alignment: .firstTextBaseline, spacing: 14) {
                            Text(num)
                                .font(.headline.monospacedDigit())
                                .foregroundStyle(.secondary)
                                .frame(width: 18, alignment: .leading)
                            Text(text)
                        }
                        .padding(.vertical, 2)
                    }
                } header: {
                    Text("Daily Automation")
                } footer: {
                    Text("This is the one-time iOS step that lets the shortcut run automatically every night without a tap.")
                }

                Section {
                    Button {
                        ShortcutLauncher.openShortcutsApp()
                    } label: {
                        Label("Open Shortcuts", systemImage: "arrow.up.right.square")
                            .frame(maxWidth: .infinity, alignment: .center)
                    }
                    .buttonStyle(.borderedProminent)
                    .listRowBackground(Color.clear)
                }
            }
            .navigationTitle("Daily Automation")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}

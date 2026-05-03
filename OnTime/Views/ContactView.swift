import SwiftUI

struct ContactView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section {
                    contactRow(
                        title: "Email",
                        value: AppConstants.contactEmail,
                        url: URL(string: "mailto:\(AppConstants.contactEmail)")
                    )
                    contactRow(
                        title: "Phone",
                        value: formatted(AppConstants.contactPhone),
                        url: URL(string: "tel:\(AppConstants.contactPhone)")
                    )
                    contactRow(
                        title: "GitHub",
                        value: "rsktaker/on-time",
                        url: URL(string: AppConstants.supportURL)
                    )
                } footer: {
                    Text("Reach out with questions, ideas, or bugs. This is a one-person project.")
                }
            }
            .navigationTitle("Contact")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    @ViewBuilder
    private func contactRow(title: String, value: String, url: URL?) -> some View {
        if let url {
            Link(destination: url) {
                HStack {
                    Text(title).foregroundStyle(.primary)
                    Spacer()
                    Text(value).foregroundStyle(.secondary)
                }
            }
        } else {
            HStack {
                Text(title)
                Spacer()
                Text(value).foregroundStyle(.secondary)
            }
        }
    }

    private func formatted(_ digits: String) -> String {
        let d = digits.filter(\.isNumber)
        guard d.count == 10 else { return digits }
        let area = d.prefix(3)
        let mid = d.dropFirst(3).prefix(3)
        let last = d.suffix(4)
        return "(\(area)) \(mid)-\(last)"
    }
}

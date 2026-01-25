import SwiftUI

// MARK: - Color Extensions
extension Color {
    static let appPrimary = Color.blue
    static let appSecondary = Color.purple
    static let appAccent = Color.orange

    static let gradientStart = Color.blue
    static let gradientEnd = Color.purple

    static var appGradient: LinearGradient {
        LinearGradient(
            colors: [.gradientStart, .gradientEnd],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}

// MARK: - View Extensions
extension View {
    func cardStyle() -> some View {
        self
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }

    func hideKeyboard() {
        UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
    }

    @ViewBuilder
    func `if`<Content: View>(_ condition: Bool, transform: (Self) -> Content) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

// MARK: - Date Extensions
extension Date {
    var isToday: Bool {
        Calendar.current.isDateInToday(self)
    }

    var isYesterday: Bool {
        Calendar.current.isDateInYesterday(self)
    }

    var relativeString: String {
        if isToday {
            return "Heute, " + formatted(date: .omitted, time: .shortened)
        } else if isYesterday {
            return "Gestern, " + formatted(date: .omitted, time: .shortened)
        } else {
            return formatted(date: .abbreviated, time: .shortened)
        }
    }

    var shortRelativeString: String {
        if isToday {
            return formatted(date: .omitted, time: .shortened)
        } else if isYesterday {
            return "Gestern"
        } else if Calendar.current.isDate(self, equalTo: Date(), toGranularity: .weekOfYear) {
            let formatter = DateFormatter()
            formatter.locale = Locale(identifier: "de_DE")
            formatter.dateFormat = "EEEE"
            return formatter.string(from: self)
        } else {
            return formatted(date: .abbreviated, time: .omitted)
        }
    }
}

// MARK: - String Extensions
extension String {
    var trimmed: String {
        trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var isNotEmpty: Bool {
        !isEmpty
    }

    func truncated(to length: Int, trailing: String = "...") -> String {
        if count > length {
            return String(prefix(length)) + trailing
        }
        return self
    }
}

// MARK: - Array Extensions
extension Array where Element == Note {
    func sortedByDate(ascending: Bool = false) -> [Note] {
        sorted { ascending ? $0.updatedAt < $1.updatedAt : $0.updatedAt > $1.updatedAt }
    }

    func sortedByPriority() -> [Note] {
        sorted { priorityValue($0.priority) > priorityValue($1.priority) }
    }

    private func priorityValue(_ priority: Priority) -> Int {
        switch priority {
        case .low: return 0
        case .normal: return 1
        case .high: return 2
        case .urgent: return 3
        }
    }
}

// MARK: - Haptic Feedback
enum HapticFeedback {
    case light
    case medium
    case heavy
    case success
    case warning
    case error

    func trigger() {
        switch self {
        case .light:
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        case .medium:
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        case .heavy:
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
        case .success:
            UINotificationFeedbackGenerator().notificationOccurred(.success)
        case .warning:
            UINotificationFeedbackGenerator().notificationOccurred(.warning)
        case .error:
            UINotificationFeedbackGenerator().notificationOccurred(.error)
        }
    }
}

// MARK: - App Constants
enum AppConstants {
    static let appName = "Voice Notes"
    static let appGroupID = "group.com.voicenotes.app"
    static let bundleID = "com.voicenotes.app"

    enum Keys {
        static let savedNotes = "savedNotes"
        static let lastSyncDate = "lastSyncDate"
        static let userPreferences = "userPreferences"
    }

    enum Limits {
        static let maxTitleLength = 100
        static let maxContentLength = 10000
        static let maxTags = 10
    }
}

// MARK: - Notification Names
extension Notification.Name {
    static let noteDidChange = Notification.Name("noteDidChange")
    static let noteDidDelete = Notification.Name("noteDidDelete")
    static let notesDidSync = Notification.Name("notesDidSync")
}

// MARK: - Preview Helpers
#if DEBUG
extension Note {
    static var preview: Note {
        Note(
            title: "Preview Notiz",
            content: "Dies ist eine Vorschau-Notiz für SwiftUI Previews.",
            isPinned: true,
            priority: .high,
            category: .work,
            isTodo: true,
            tags: ["preview", "test"]
        )
    }
}
#endif

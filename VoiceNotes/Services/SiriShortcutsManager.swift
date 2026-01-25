import Foundation
import Intents
import IntentsUI
import SwiftUI

// MARK: - Siri Shortcuts Manager
class SiriShortcutsManager: ObservableObject {
    static let shared = SiriShortcutsManager()

    // MARK: - Activity Types
    enum ActivityType: String {
        case createNote = "com.voicenotes.app.createNote"
        case createTodo = "com.voicenotes.app.createTodo"
        case viewNotes = "com.voicenotes.app.viewNotes"
        case voiceInput = "com.voicenotes.app.voiceInput"
    }

    // MARK: - Create User Activities

    func createNoteActivity() -> NSUserActivity {
        let activity = NSUserActivity(activityType: ActivityType.createNote.rawValue)
        activity.title = "Neue Notiz erstellen"
        activity.suggestedInvocationPhrase = "Neue Notiz"
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        activity.persistentIdentifier = ActivityType.createNote.rawValue
        return activity
    }

    func createTodoActivity() -> NSUserActivity {
        let activity = NSUserActivity(activityType: ActivityType.createTodo.rawValue)
        activity.title = "Neue Aufgabe erstellen"
        activity.suggestedInvocationPhrase = "Neue Aufgabe"
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        activity.persistentIdentifier = ActivityType.createTodo.rawValue
        return activity
    }

    func viewNotesActivity() -> NSUserActivity {
        let activity = NSUserActivity(activityType: ActivityType.viewNotes.rawValue)
        activity.title = "Notizen anzeigen"
        activity.suggestedInvocationPhrase = "Zeige meine Notizen"
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        activity.persistentIdentifier = ActivityType.viewNotes.rawValue
        return activity
    }

    func voiceInputActivity() -> NSUserActivity {
        let activity = NSUserActivity(activityType: ActivityType.voiceInput.rawValue)
        activity.title = "Spracheingabe starten"
        activity.suggestedInvocationPhrase = "Sprachnotiz"
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        activity.persistentIdentifier = ActivityType.voiceInput.rawValue
        return activity
    }

    // MARK: - Donate Shortcuts

    func donateCreateNoteShortcut() {
        let activity = createNoteActivity()
        activity.becomeCurrent()
    }

    func donateCreateTodoShortcut() {
        let activity = createTodoActivity()
        activity.becomeCurrent()
    }

    func donateViewNotesShortcut() {
        let activity = viewNotesActivity()
        activity.becomeCurrent()
    }

    func donateVoiceInputShortcut() {
        let activity = voiceInputActivity()
        activity.becomeCurrent()
    }

    // MARK: - Handle Activity

    func handleActivity(_ activity: NSUserActivity) -> ShortcutAction? {
        guard let activityType = ActivityType(rawValue: activity.activityType) else {
            return nil
        }

        switch activityType {
        case .createNote:
            return .createNote
        case .createTodo:
            return .createTodo
        case .viewNotes:
            return .viewNotes
        case .voiceInput:
            return .voiceInput
        }
    }
}

// MARK: - Shortcut Action
enum ShortcutAction {
    case createNote
    case createTodo
    case viewNotes
    case voiceInput
}

// MARK: - Siri Tip View
struct SiriTipView: View {
    let phrase: String
    let description: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "waveform.circle.fill")
                .font(.system(size: 40))
                .foregroundStyle(.linearGradient(
                    colors: [.purple, .blue],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ))

            VStack(alignment: .leading, spacing: 4) {
                Text("Siri Shortcut")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Text("\"\(phrase)\"")
                    .font(.headline)

                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Shortcuts Settings View
struct ShortcutsSettingsView: View {
    @StateObject private var shortcutsManager = SiriShortcutsManager.shared

    var body: some View {
        List {
            Section(header: Text("Verfügbare Siri Shortcuts")) {
                SiriShortcutRow(
                    title: "Neue Notiz",
                    phrase: "Neue Notiz",
                    icon: "note.text.badge.plus",
                    color: .blue
                ) {
                    shortcutsManager.donateCreateNoteShortcut()
                }

                SiriShortcutRow(
                    title: "Neue Aufgabe",
                    phrase: "Neue Aufgabe",
                    icon: "checklist",
                    color: .green
                ) {
                    shortcutsManager.donateCreateTodoShortcut()
                }

                SiriShortcutRow(
                    title: "Notizen anzeigen",
                    phrase: "Zeige meine Notizen",
                    icon: "list.bullet",
                    color: .purple
                ) {
                    shortcutsManager.donateViewNotesShortcut()
                }

                SiriShortcutRow(
                    title: "Spracheingabe",
                    phrase: "Sprachnotiz",
                    icon: "mic.fill",
                    color: .orange
                ) {
                    shortcutsManager.donateVoiceInputShortcut()
                }
            }

            Section(footer: Text("Tippe auf einen Shortcut um ihn zu Siri hinzuzufügen. Du kannst dann mit dem angezeigten Sprachbefehl die Aktion ausführen.")) {
                EmptyView()
            }
        }
        .navigationTitle("Siri Shortcuts")
    }
}

// MARK: - Siri Shortcut Row
struct SiriShortcutRow: View {
    let title: String
    let phrase: String
    let icon: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 40, height: 40)
                    .background(color)
                    .cornerRadius(8)

                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text("„\(phrase)"")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "plus.circle.fill")
                    .foregroundColor(color)
            }
            .padding(.vertical, 4)
        }
    }
}

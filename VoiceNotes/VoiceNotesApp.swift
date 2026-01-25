import SwiftUI

@main
struct VoiceNotesApp: App {
    @StateObject private var dataService = DataService.shared
    @State private var shortcutAction: ShortcutAction?

    var body: some Scene {
        WindowGroup {
            ContentView(shortcutAction: $shortcutAction)
                .environmentObject(dataService)
                .onContinueUserActivity("com.voicenotes.app.createNote") { _ in
                    shortcutAction = .createNote
                }
                .onContinueUserActivity("com.voicenotes.app.createTodo") { _ in
                    shortcutAction = .createTodo
                }
                .onContinueUserActivity("com.voicenotes.app.viewNotes") { _ in
                    shortcutAction = .viewNotes
                }
                .onContinueUserActivity("com.voicenotes.app.voiceInput") { _ in
                    shortcutAction = .voiceInput
                }
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }

    private func handleDeepLink(_ url: URL) {
        guard let host = url.host else { return }

        switch host {
        case "new":
            shortcutAction = .createNote
        case "todo":
            shortcutAction = .createTodo
        case "voice":
            shortcutAction = .voiceInput
        default:
            break
        }
    }
}

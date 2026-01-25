import Foundation
import WidgetKit

// MARK: - Data Service
class DataService: ObservableObject {
    static let shared = DataService()

    private let notesKey = "savedNotes"
    private let userDefaults: UserDefaults

    @Published var notes: [Note] = []

    init() {
        // Use App Group for sharing data with Widget
        if let groupDefaults = UserDefaults(suiteName: "group.com.voicenotes.app") {
            self.userDefaults = groupDefaults
        } else {
            self.userDefaults = UserDefaults.standard
        }
        loadNotes()
    }

    // MARK: - CRUD Operations

    func loadNotes() {
        guard let data = userDefaults.data(forKey: notesKey) else {
            // Load sample notes on first launch
            notes = Note.sampleNotes
            saveNotes()
            return
        }

        do {
            let decoder = JSONDecoder()
            notes = try decoder.decode([Note].self, from: data)
        } catch {
            print("Error loading notes: \(error)")
            notes = []
        }
    }

    func saveNotes() {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(notes)
            userDefaults.set(data, forKey: notesKey)

            // Refresh widgets when data changes
            WidgetCenter.shared.reloadAllTimelines()
        } catch {
            print("Error saving notes: \(error)")
        }
    }

    func addNote(_ note: Note) {
        notes.insert(note, at: 0)
        saveNotes()
    }

    func updateNote(_ note: Note) {
        if let index = notes.firstIndex(where: { $0.id == note.id }) {
            var updatedNote = note
            updatedNote.updatedAt = Date()
            notes[index] = updatedNote
            saveNotes()
        }
    }

    func deleteNote(_ note: Note) {
        notes.removeAll { $0.id == note.id }
        saveNotes()
    }

    func deleteNotes(at offsets: IndexSet) {
        notes.remove(atOffsets: offsets)
        saveNotes()
    }

    func togglePinned(_ note: Note) {
        if let index = notes.firstIndex(where: { $0.id == note.id }) {
            notes[index].isPinned.toggle()
            saveNotes()
        }
    }

    func toggleCompleted(_ note: Note) {
        if let index = notes.firstIndex(where: { $0.id == note.id }) {
            notes[index].isCompleted.toggle()
            notes[index].updatedAt = Date()
            saveNotes()
        }
    }

    // MARK: - Filtering & Sorting

    var pinnedNotes: [Note] {
        notes.filter { $0.isPinned }
    }

    var unpinnedNotes: [Note] {
        notes.filter { !$0.isPinned }
    }

    var todoNotes: [Note] {
        notes.filter { $0.isTodo }
    }

    var completedTodos: [Note] {
        notes.filter { $0.isTodo && $0.isCompleted }
    }

    var incompleteTodos: [Note] {
        notes.filter { $0.isTodo && !$0.isCompleted }
    }

    func notes(for category: Category) -> [Note] {
        notes.filter { $0.category == category }
    }

    func notes(with priority: Priority) -> [Note] {
        notes.filter { $0.priority == priority }
    }

    func searchNotes(query: String) -> [Note] {
        guard !query.isEmpty else { return notes }
        let lowercasedQuery = query.lowercased()
        return notes.filter {
            $0.title.lowercased().contains(lowercasedQuery) ||
            $0.content.lowercased().contains(lowercasedQuery) ||
            $0.tags.contains { $0.lowercased().contains(lowercasedQuery) }
        }
    }

    // MARK: - Quick Add from Voice

    func addQuickNote(title: String, content: String, asTodo: Bool = false) -> Note {
        let note = Note(
            title: title,
            content: content,
            isTodo: asTodo
        )
        addNote(note)
        return note
    }

    // MARK: - Statistics

    var totalNotesCount: Int {
        notes.count
    }

    var todoCompletionPercentage: Double {
        let todos = todoNotes
        guard !todos.isEmpty else { return 0 }
        let completed = todos.filter { $0.isCompleted }.count
        return Double(completed) / Double(todos.count) * 100
    }
}

// MARK: - Shared Data for Widget
extension DataService {
    func getRecentNotes(limit: Int = 5) -> [Note] {
        Array(notes.sorted { $0.updatedAt > $1.updatedAt }.prefix(limit))
    }

    func getUpcomingTodos(limit: Int = 3) -> [Note] {
        Array(incompleteTodos.prefix(limit))
    }

    static func loadNotesForWidget() -> [Note] {
        guard let groupDefaults = UserDefaults(suiteName: "group.com.voicenotes.app"),
              let data = groupDefaults.data(forKey: "savedNotes") else {
            return Note.sampleNotes
        }

        do {
            let decoder = JSONDecoder()
            return try decoder.decode([Note].self, from: data)
        } catch {
            return Note.sampleNotes
        }
    }
}

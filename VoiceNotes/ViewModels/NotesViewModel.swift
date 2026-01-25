import Foundation
import SwiftUI
import Combine

// MARK: - Notes ViewModel
@MainActor
class NotesViewModel: ObservableObject {
    @Published var notes: [Note] = []
    @Published var searchText: String = ""
    @Published var selectedCategory: Category?
    @Published var selectedPriority: Priority?
    @Published var showCompletedTodos: Bool = true
    @Published var sortOption: SortOption = .dateUpdated
    @Published var isLoading: Bool = false

    private let dataService = DataService.shared
    private var cancellables = Set<AnyCancellable>()

    init() {
        setupBindings()
        loadNotes()
    }

    // MARK: - Setup

    private func setupBindings() {
        dataService.$notes
            .receive(on: DispatchQueue.main)
            .sink { [weak self] notes in
                self?.notes = notes
            }
            .store(in: &cancellables)
    }

    func loadNotes() {
        isLoading = true
        dataService.loadNotes()
        isLoading = false
    }

    // MARK: - Filtered & Sorted Notes

    var filteredNotes: [Note] {
        var result = notes

        // Search filter
        if !searchText.isEmpty {
            result = dataService.searchNotes(query: searchText)
        }

        // Category filter
        if let category = selectedCategory {
            result = result.filter { $0.category == category }
        }

        // Priority filter
        if let priority = selectedPriority {
            result = result.filter { $0.priority == priority }
        }

        // Hide completed todos if setting is off
        if !showCompletedTodos {
            result = result.filter { !$0.isCompleted }
        }

        // Sort
        return sortNotes(result)
    }

    var pinnedNotes: [Note] {
        filteredNotes.filter { $0.isPinned }
    }

    var unpinnedNotes: [Note] {
        filteredNotes.filter { !$0.isPinned }
    }

    private func sortNotes(_ notes: [Note]) -> [Note] {
        switch sortOption {
        case .dateCreated:
            return notes.sorted { $0.createdAt > $1.createdAt }
        case .dateUpdated:
            return notes.sorted { $0.updatedAt > $1.updatedAt }
        case .title:
            return notes.sorted { $0.title.localizedCompare($1.title) == .orderedAscending }
        case .priority:
            return notes.sorted { priorityValue($0.priority) > priorityValue($1.priority) }
        }
    }

    private func priorityValue(_ priority: Priority) -> Int {
        switch priority {
        case .low: return 0
        case .normal: return 1
        case .high: return 2
        case .urgent: return 3
        }
    }

    // MARK: - CRUD Operations

    func addNote(_ note: Note) {
        dataService.addNote(note)
    }

    func updateNote(_ note: Note) {
        dataService.updateNote(note)
    }

    func deleteNote(_ note: Note) {
        dataService.deleteNote(note)
    }

    func deleteNotes(at offsets: IndexSet) {
        dataService.deleteNotes(at: offsets)
    }

    func togglePinned(_ note: Note) {
        dataService.togglePinned(note)
    }

    func toggleCompleted(_ note: Note) {
        dataService.toggleCompleted(note)
    }

    // MARK: - Quick Actions

    func createQuickNote(title: String, content: String, asTodo: Bool = false) {
        let note = Note(
            title: title.isEmpty ? "Neue Notiz" : title,
            content: content,
            isTodo: asTodo
        )
        addNote(note)
    }

    func createVoiceNote(transcribedText: String) {
        let lines = transcribedText.components(separatedBy: "\n")
        let title = lines.first ?? "Sprachnotiz"
        let content = lines.dropFirst().joined(separator: "\n")

        let note = Note(
            title: title,
            content: content.isEmpty ? transcribedText : content,
            tags: ["sprachnotiz"]
        )
        addNote(note)
    }

    // MARK: - Statistics

    var totalCount: Int {
        notes.count
    }

    var todoCount: Int {
        notes.filter { $0.isTodo }.count
    }

    var completedTodoCount: Int {
        notes.filter { $0.isTodo && $0.isCompleted }.count
    }

    var completionPercentage: Double {
        guard todoCount > 0 else { return 0 }
        return Double(completedTodoCount) / Double(todoCount) * 100
    }

    // MARK: - Clear Filters

    func clearFilters() {
        searchText = ""
        selectedCategory = nil
        selectedPriority = nil
    }

    var hasActiveFilters: Bool {
        !searchText.isEmpty || selectedCategory != nil || selectedPriority != nil
    }
}

// MARK: - Sort Option
enum SortOption: String, CaseIterable {
    case dateUpdated = "Zuletzt bearbeitet"
    case dateCreated = "Erstellungsdatum"
    case title = "Titel"
    case priority = "Priorität"

    var icon: String {
        switch self {
        case .dateUpdated: return "clock.arrow.circlepath"
        case .dateCreated: return "calendar"
        case .title: return "textformat"
        case .priority: return "exclamationmark.triangle"
        }
    }
}

import SwiftUI

// MARK: - Note List View
struct NoteListView: View {
    @StateObject private var viewModel = NotesViewModel()
    @State private var showingNewNote = false
    @State private var showingVoiceInput = false
    @State private var showingFilters = false
    @State private var selectedNote: Note?
    @State private var viewMode: ViewMode = .list

    var body: some View {
        NavigationStack {
            ZStack {
                // Background
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()

                VStack(spacing: 0) {
                    // Search Bar
                    SearchBar(text: $viewModel.searchText)
                        .padding(.horizontal)
                        .padding(.top, 8)

                    // Filter Pills
                    if viewModel.hasActiveFilters {
                        ActiveFiltersView(viewModel: viewModel)
                    }

                    // Stats Header
                    StatsHeaderView(viewModel: viewModel)
                        .padding(.horizontal)
                        .padding(.vertical, 8)

                    // Content
                    if viewModel.filteredNotes.isEmpty {
                        EmptyStateView(
                            hasFilters: viewModel.hasActiveFilters,
                            onClearFilters: { viewModel.clearFilters() }
                        )
                    } else {
                        notesList
                    }
                }

                // Floating Action Buttons
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        FloatingActionButtons(
                            onVoice: { showingVoiceInput = true },
                            onNew: { showingNewNote = true }
                        )
                        .padding()
                    }
                }
            }
            .navigationTitle("Notizen")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Picker("Ansicht", selection: $viewMode) {
                            Label("Liste", systemImage: "list.bullet").tag(ViewMode.list)
                            Label("Raster", systemImage: "square.grid.2x2").tag(ViewMode.grid)
                        }
                    } label: {
                        Image(systemName: viewMode == .list ? "list.bullet" : "square.grid.2x2")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    HStack {
                        // Sort Menu
                        Menu {
                            ForEach(SortOption.allCases, id: \.self) { option in
                                Button {
                                    viewModel.sortOption = option
                                } label: {
                                    Label(option.rawValue, systemImage: option.icon)
                                    if viewModel.sortOption == option {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }
                        } label: {
                            Image(systemName: "arrow.up.arrow.down")
                        }

                        // Filter Button
                        Button {
                            showingFilters = true
                        } label: {
                            Image(systemName: viewModel.hasActiveFilters ? "line.3.horizontal.decrease.circle.fill" : "line.3.horizontal.decrease.circle")
                        }
                    }
                }
            }
            .sheet(isPresented: $showingNewNote) {
                NoteEditorView(mode: .create) { note in
                    viewModel.addNote(note)
                }
            }
            .sheet(isPresented: $showingVoiceInput) {
                VoiceInputView { text in
                    if text.hasPrefix("TODO:") {
                        let content = String(text.dropFirst(5))
                        viewModel.createQuickNote(title: "Aufgabe", content: content, asTodo: true)
                    } else {
                        viewModel.createVoiceNote(transcribedText: text)
                    }
                }
            }
            .sheet(isPresented: $showingFilters) {
                FilterView(viewModel: viewModel)
                    .presentationDetents([.medium])
            }
            .sheet(item: $selectedNote) { note in
                NoteDetailView(note: note, viewModel: viewModel)
            }
        }
    }

    // MARK: - Notes List
    private var notesList: some View {
        Group {
            if viewMode == .list {
                List {
                    // Pinned Section
                    if !viewModel.pinnedNotes.isEmpty {
                        Section(header: Label("Angepinnt", systemImage: "pin.fill")) {
                            ForEach(viewModel.pinnedNotes) { note in
                                NoteRowView(note: note, viewModel: viewModel)
                                    .onTapGesture {
                                        selectedNote = note
                                    }
                            }
                            .onDelete { offsets in
                                deleteNotes(from: viewModel.pinnedNotes, at: offsets)
                            }
                        }
                    }

                    // All Notes Section
                    Section(header: Text("Alle Notizen")) {
                        ForEach(viewModel.unpinnedNotes) { note in
                            NoteRowView(note: note, viewModel: viewModel)
                                .onTapGesture {
                                    selectedNote = note
                                }
                        }
                        .onDelete { offsets in
                            deleteNotes(from: viewModel.unpinnedNotes, at: offsets)
                        }
                    }
                }
                .listStyle(.insetGrouped)
            } else {
                ScrollView {
                    LazyVGrid(columns: [
                        GridItem(.flexible(), spacing: 12),
                        GridItem(.flexible(), spacing: 12)
                    ], spacing: 12) {
                        ForEach(viewModel.filteredNotes) { note in
                            NoteGridCard(note: note) {
                                viewModel.toggleCompleted(note)
                            }
                            .onTapGesture {
                                selectedNote = note
                            }
                        }
                    }
                    .padding()
                }
            }
        }
    }

    private func deleteNotes(from notes: [Note], at offsets: IndexSet) {
        for index in offsets {
            viewModel.deleteNote(notes[index])
        }
    }
}

// MARK: - View Mode
enum ViewMode {
    case list
    case grid
}

// MARK: - Note Row View
struct NoteRowView: View {
    let note: Note
    @ObservedObject var viewModel: NotesViewModel

    var body: some View {
        HStack(spacing: 12) {
            // Category Icon
            Image(systemName: note.category.icon)
                .font(.body)
                .foregroundColor(.white)
                .frame(width: 36, height: 36)
                .background(note.category.color)
                .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(note.title.isEmpty ? "Ohne Titel" : note.title)
                        .font(.headline)
                        .lineLimit(1)
                        .strikethrough(note.isCompleted)
                        .foregroundColor(note.isCompleted ? .secondary : .primary)

                    if note.priority != .normal {
                        Image(systemName: note.priority.icon)
                            .font(.caption)
                            .foregroundColor(note.priority.color)
                    }
                }

                Text(note.content)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }

            Spacer()

            if note.isTodo {
                Button {
                    viewModel.toggleCompleted(note)
                } label: {
                    Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                        .font(.title2)
                        .foregroundColor(note.isCompleted ? .green : .gray)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 4)
        .swipeActions(edge: .leading) {
            Button {
                viewModel.togglePinned(note)
            } label: {
                Label(note.isPinned ? "Lösen" : "Anpinnen", systemImage: note.isPinned ? "pin.slash" : "pin")
            }
            .tint(.orange)
        }
        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
            Button(role: .destructive) {
                viewModel.deleteNote(note)
            } label: {
                Label("Löschen", systemImage: "trash")
            }
        }
    }
}

// MARK: - Search Bar
struct SearchBar: View {
    @Binding var text: String

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)

            TextField("Notizen durchsuchen...", text: $text)

            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(12)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Stats Header View
struct StatsHeaderView: View {
    @ObservedObject var viewModel: NotesViewModel

    var body: some View {
        HStack(spacing: 16) {
            StatBadge(title: "Gesamt", value: "\(viewModel.totalCount)", icon: "doc.text", color: .blue)
            StatBadge(title: "Aufgaben", value: "\(viewModel.completedTodoCount)/\(viewModel.todoCount)", icon: "checkmark.circle", color: .green)
            if viewModel.todoCount > 0 {
                StatBadge(title: "Erledigt", value: String(format: "%.0f%%", viewModel.completionPercentage), icon: "chart.pie", color: .purple)
            }
        }
    }
}

struct StatBadge: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption)
                .foregroundColor(color)

            VStack(alignment: .leading, spacing: 0) {
                Text(value)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text(title)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

// MARK: - Active Filters View
struct ActiveFiltersView: View {
    @ObservedObject var viewModel: NotesViewModel

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                if let category = viewModel.selectedCategory {
                    FilterChip(title: category.rawValue, color: category.color) {
                        viewModel.selectedCategory = nil
                    }
                }

                if let priority = viewModel.selectedPriority {
                    FilterChip(title: priority.rawValue, color: priority.color) {
                        viewModel.selectedPriority = nil
                    }
                }

                if !viewModel.searchText.isEmpty {
                    FilterChip(title: "Suche: \(viewModel.searchText)", color: .gray) {
                        viewModel.searchText = ""
                    }
                }

                Button {
                    viewModel.clearFilters()
                } label: {
                    Text("Alle löschen")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
    }
}

struct FilterChip: View {
    let title: String
    let color: Color
    let onRemove: () -> Void

    var body: some View {
        HStack(spacing: 4) {
            Text(title)
                .font(.caption)

            Button(action: onRemove) {
                Image(systemName: "xmark.circle.fill")
                    .font(.caption)
            }
        }
        .foregroundColor(color)
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(color.opacity(0.15))
        .cornerRadius(16)
    }
}

// MARK: - Empty State View
struct EmptyStateView: View {
    let hasFilters: Bool
    let onClearFilters: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Spacer()

            Image(systemName: hasFilters ? "magnifyingglass" : "note.text")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text(hasFilters ? "Keine Ergebnisse" : "Noch keine Notizen")
                .font(.title2)
                .fontWeight(.semibold)

            Text(hasFilters ? "Versuche andere Filter" : "Erstelle deine erste Notiz mit dem + Button oder nutze die Sprachaufnahme")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)

            if hasFilters {
                Button("Filter zurücksetzen") {
                    onClearFilters()
                }
                .buttonStyle(.bordered)
            }

            Spacer()
        }
    }
}

// MARK: - Floating Action Buttons
struct FloatingActionButtons: View {
    let onVoice: () -> Void
    let onNew: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            // Voice Button
            Button(action: onVoice) {
                Image(systemName: "mic.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(
                        LinearGradient(
                            colors: [.purple, .blue],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .clipShape(Circle())
                    .shadow(color: .purple.opacity(0.4), radius: 8, x: 0, y: 4)
            }

            // New Note Button
            Button(action: onNew) {
                Image(systemName: "plus")
                    .font(.title)
                    .foregroundColor(.white)
                    .frame(width: 60, height: 60)
                    .background(Color.blue)
                    .clipShape(Circle())
                    .shadow(color: .blue.opacity(0.4), radius: 8, x: 0, y: 4)
            }
        }
    }
}

// MARK: - Filter View
struct FilterView: View {
    @ObservedObject var viewModel: NotesViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            List {
                Section("Kategorie") {
                    ForEach(Category.allCases, id: \.self) { category in
                        Button {
                            if viewModel.selectedCategory == category {
                                viewModel.selectedCategory = nil
                            } else {
                                viewModel.selectedCategory = category
                            }
                        } label: {
                            HStack {
                                Image(systemName: category.icon)
                                    .foregroundColor(category.color)
                                Text(category.rawValue)
                                    .foregroundColor(.primary)
                                Spacer()
                                if viewModel.selectedCategory == category {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                        }
                    }
                }

                Section("Priorität") {
                    ForEach(Priority.allCases, id: \.self) { priority in
                        Button {
                            if viewModel.selectedPriority == priority {
                                viewModel.selectedPriority = nil
                            } else {
                                viewModel.selectedPriority = priority
                            }
                        } label: {
                            HStack {
                                Image(systemName: priority.icon)
                                    .foregroundColor(priority.color)
                                Text(priority.rawValue)
                                    .foregroundColor(.primary)
                                Spacer()
                                if viewModel.selectedPriority == priority {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.blue)
                                }
                            }
                        }
                    }
                }

                Section {
                    Toggle("Erledigte Aufgaben anzeigen", isOn: $viewModel.showCompletedTodos)
                }
            }
            .navigationTitle("Filter")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Fertig") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Preview
#Preview {
    NoteListView()
}

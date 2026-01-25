import SwiftUI

struct ContentView: View {
    @EnvironmentObject var dataService: DataService
    @Binding var shortcutAction: ShortcutAction?

    @State private var selectedTab: Tab = .notes
    @State private var showingNewNote = false
    @State private var showingNewTodo = false
    @State private var showingVoiceInput = false

    enum Tab {
        case notes
        case todos
        case settings
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            // Notes Tab
            NoteListView()
                .tabItem {
                    Label("Notizen", systemImage: "note.text")
                }
                .tag(Tab.notes)

            // Todos Tab
            TodoListView()
                .tabItem {
                    Label("Aufgaben", systemImage: "checklist")
                }
                .tag(Tab.todos)

            // Settings Tab
            SettingsView()
                .tabItem {
                    Label("Einstellungen", systemImage: "gearshape")
                }
                .tag(Tab.settings)
        }
        .tint(.blue)
        .onChange(of: shortcutAction) { _, action in
            handleShortcutAction(action)
        }
        .sheet(isPresented: $showingNewNote) {
            NoteEditorView(mode: .create) { note in
                dataService.addNote(note)
            }
        }
        .sheet(isPresented: $showingNewTodo) {
            NoteEditorView(mode: .create) { note in
                var todoNote = note
                todoNote.isTodo = true
                dataService.addNote(todoNote)
            }
        }
        .sheet(isPresented: $showingVoiceInput) {
            VoiceInputView { text in
                let note = Note(
                    title: text.components(separatedBy: "\n").first ?? "Sprachnotiz",
                    content: text,
                    tags: ["sprachnotiz"]
                )
                dataService.addNote(note)
            }
        }
    }

    private func handleShortcutAction(_ action: ShortcutAction?) {
        guard let action = action else { return }

        switch action {
        case .createNote:
            selectedTab = .notes
            showingNewNote = true
        case .createTodo:
            selectedTab = .todos
            showingNewTodo = true
        case .viewNotes:
            selectedTab = .notes
        case .voiceInput:
            showingVoiceInput = true
        }

        // Reset action
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            shortcutAction = nil
        }
    }
}

// MARK: - Todo List View
struct TodoListView: View {
    @StateObject private var viewModel = NotesViewModel()
    @State private var showingNewTodo = false

    var todos: [Note] {
        viewModel.notes.filter { $0.isTodo }
    }

    var incompleteTodos: [Note] {
        todos.filter { !$0.isCompleted }
    }

    var completedTodos: [Note] {
        todos.filter { $0.isCompleted }
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()

                if todos.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "checklist")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)

                        Text("Keine Aufgaben")
                            .font(.title2)
                            .fontWeight(.semibold)

                        Text("Erstelle deine erste Aufgabe")
                            .foregroundColor(.secondary)

                        Button {
                            showingNewTodo = true
                        } label: {
                            Label("Neue Aufgabe", systemImage: "plus")
                        }
                        .buttonStyle(.borderedProminent)
                    }
                } else {
                    List {
                        // Progress Section
                        Section {
                            TodoProgressView(
                                completed: completedTodos.count,
                                total: todos.count
                            )
                        }

                        // Incomplete Todos
                        if !incompleteTodos.isEmpty {
                            Section(header: Text("Offen (\(incompleteTodos.count))")) {
                                ForEach(incompleteTodos) { todo in
                                    TodoRow(todo: todo, viewModel: viewModel)
                                }
                                .onDelete { offsets in
                                    deleteTodos(from: incompleteTodos, at: offsets)
                                }
                            }
                        }

                        // Completed Todos
                        if !completedTodos.isEmpty {
                            Section(header: Text("Erledigt (\(completedTodos.count))")) {
                                ForEach(completedTodos) { todo in
                                    TodoRow(todo: todo, viewModel: viewModel)
                                }
                                .onDelete { offsets in
                                    deleteTodos(from: completedTodos, at: offsets)
                                }
                            }
                        }
                    }
                    .listStyle(.insetGrouped)
                }

                // FAB
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Button {
                            showingNewTodo = true
                        } label: {
                            Image(systemName: "plus")
                                .font(.title2)
                                .foregroundColor(.white)
                                .frame(width: 60, height: 60)
                                .background(Color.green)
                                .clipShape(Circle())
                                .shadow(color: .green.opacity(0.4), radius: 8, x: 0, y: 4)
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Aufgaben")
            .sheet(isPresented: $showingNewTodo) {
                NoteEditorView(mode: .create) { note in
                    var todoNote = note
                    todoNote.isTodo = true
                    viewModel.addNote(todoNote)
                }
            }
        }
    }

    private func deleteTodos(from todos: [Note], at offsets: IndexSet) {
        for index in offsets {
            viewModel.deleteNote(todos[index])
        }
    }
}

// MARK: - Todo Row
struct TodoRow: View {
    let todo: Note
    @ObservedObject var viewModel: NotesViewModel

    var body: some View {
        HStack(spacing: 12) {
            Button {
                HapticFeedback.light.trigger()
                viewModel.toggleCompleted(todo)
            } label: {
                Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundColor(todo.isCompleted ? .green : .gray)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 4) {
                Text(todo.title.isEmpty ? "Ohne Titel" : todo.title)
                    .font(.body)
                    .strikethrough(todo.isCompleted)
                    .foregroundColor(todo.isCompleted ? .secondary : .primary)

                if !todo.content.isEmpty {
                    Text(todo.content)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }

            Spacer()

            if todo.priority != .normal {
                Image(systemName: todo.priority.icon)
                    .foregroundColor(todo.priority.color)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Todo Progress View
struct TodoProgressView: View {
    let completed: Int
    let total: Int

    var progress: Double {
        guard total > 0 else { return 0 }
        return Double(completed) / Double(total)
    }

    var body: some View {
        VStack(spacing: 12) {
            HStack {
                VStack(alignment: .leading) {
                    Text("\(completed) von \(total)")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Aufgaben erledigt")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                ZStack {
                    Circle()
                        .stroke(Color.gray.opacity(0.2), lineWidth: 8)
                        .frame(width: 60, height: 60)

                    Circle()
                        .trim(from: 0, to: progress)
                        .stroke(Color.green, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                        .frame(width: 60, height: 60)
                        .rotationEffect(.degrees(-90))
                        .animation(.easeOut(duration: 0.5), value: progress)

                    Text("\(Int(progress * 100))%")
                        .font(.caption)
                        .fontWeight(.semibold)
                }
            }

            ProgressView(value: progress)
                .tint(.green)
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Settings View
struct SettingsView: View {
    @AppStorage("enableHaptics") private var enableHaptics = true
    @AppStorage("defaultCategory") private var defaultCategory = "personal"
    @AppStorage("showCompletedTodos") private var showCompletedTodos = true

    var body: some View {
        NavigationStack {
            List {
                // App Section
                Section {
                    HStack {
                        Image(systemName: "note.text")
                            .font(.largeTitle)
                            .foregroundStyle(Color.appGradient)

                        VStack(alignment: .leading) {
                            Text("Voice Notes")
                                .font(.headline)
                            Text("Version 1.0.0")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 8)
                }

                // Preferences Section
                Section("Einstellungen") {
                    Toggle("Haptisches Feedback", isOn: $enableHaptics)

                    Picker("Standard-Kategorie", selection: $defaultCategory) {
                        ForEach(Category.allCases, id: \.self) { category in
                            Text(category.rawValue).tag(category.rawValue)
                        }
                    }

                    Toggle("Erledigte Aufgaben anzeigen", isOn: $showCompletedTodos)
                }

                // Siri Section
                Section("Siri & Shortcuts") {
                    NavigationLink {
                        ShortcutsSettingsView()
                    } label: {
                        Label("Siri Shortcuts einrichten", systemImage: "waveform.circle")
                    }
                }

                // Data Section
                Section("Daten") {
                    Button(role: .destructive) {
                        // Clear completed todos
                    } label: {
                        Label("Erledigte Aufgaben löschen", systemImage: "trash")
                    }
                }

                // About Section
                Section("Über") {
                    Link(destination: URL(string: "https://example.com/privacy")!) {
                        Label("Datenschutz", systemImage: "hand.raised")
                    }

                    Link(destination: URL(string: "https://example.com/terms")!) {
                        Label("Nutzungsbedingungen", systemImage: "doc.text")
                    }

                    NavigationLink {
                        Text("Open Source Lizenzen")
                    } label: {
                        Label("Lizenzen", systemImage: "doc.badge.gearshape")
                    }
                }
            }
            .navigationTitle("Einstellungen")
        }
    }
}

// MARK: - Preview
#Preview {
    ContentView(shortcutAction: .constant(nil))
        .environmentObject(DataService.shared)
}

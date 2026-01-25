import SwiftUI

// MARK: - Editor Mode
enum EditorMode {
    case create
    case edit(Note)

    var title: String {
        switch self {
        case .create: return "Neue Notiz"
        case .edit: return "Bearbeiten"
        }
    }
}

// MARK: - Note Editor View
struct NoteEditorView: View {
    let mode: EditorMode
    let onSave: (Note) -> Void

    @Environment(\.dismiss) private var dismiss
    @StateObject private var speechService = SpeechRecognitionService()

    @State private var title: String = ""
    @State private var content: String = ""
    @State private var category: Category = .personal
    @State private var priority: Priority = .normal
    @State private var isTodo: Bool = false
    @State private var isPinned: Bool = false
    @State private var tags: [String] = []
    @State private var newTag: String = ""
    @State private var reminderDate: Date?
    @State private var hasReminder: Bool = false

    @State private var showingVoiceInput = false
    @State private var voiceInputTarget: VoiceInputTarget = .title
    @FocusState private var focusedField: Field?

    enum Field {
        case title, content, tag
    }

    enum VoiceInputTarget {
        case title, content
    }

    init(mode: EditorMode, onSave: @escaping (Note) -> Void) {
        self.mode = mode
        self.onSave = onSave

        // Initialize state from existing note if editing
        if case .edit(let note) = mode {
            _title = State(initialValue: note.title)
            _content = State(initialValue: note.content)
            _category = State(initialValue: note.category)
            _priority = State(initialValue: note.priority)
            _isTodo = State(initialValue: note.isTodo)
            _isPinned = State(initialValue: note.isPinned)
            _tags = State(initialValue: note.tags)
            _reminderDate = State(initialValue: note.reminderDate)
            _hasReminder = State(initialValue: note.reminderDate != nil)
        }
    }

    var body: some View {
        NavigationView {
            Form {
                // Title Section
                Section {
                    HStack {
                        TextField("Titel", text: $title)
                            .focused($focusedField, equals: .title)

                        Button {
                            voiceInputTarget = .title
                            showingVoiceInput = true
                        } label: {
                            Image(systemName: "mic.fill")
                                .foregroundColor(.blue)
                        }
                    }
                } header: {
                    Label("Titel", systemImage: "textformat")
                }

                // Content Section
                Section {
                    VStack(alignment: .trailing, spacing: 8) {
                        TextEditor(text: $content)
                            .frame(minHeight: 150)
                            .focused($focusedField, equals: .content)

                        Button {
                            voiceInputTarget = .content
                            showingVoiceInput = true
                        } label: {
                            Label("Spracheingabe", systemImage: "mic.fill")
                                .font(.caption)
                        }
                        .buttonStyle(.bordered)
                    }
                } header: {
                    Label("Inhalt", systemImage: "doc.text")
                }

                // Category & Priority Section
                Section {
                    Picker("Kategorie", selection: $category) {
                        ForEach(Category.allCases, id: \.self) { cat in
                            Label(cat.rawValue, systemImage: cat.icon)
                                .tag(cat)
                        }
                    }

                    Picker("Priorität", selection: $priority) {
                        ForEach(Priority.allCases, id: \.self) { prio in
                            Label(prio.rawValue, systemImage: prio.icon)
                                .tag(prio)
                        }
                    }
                } header: {
                    Label("Einstellungen", systemImage: "slider.horizontal.3")
                }

                // Options Section
                Section {
                    Toggle(isOn: $isTodo) {
                        Label("Als Aufgabe markieren", systemImage: "checklist")
                    }

                    Toggle(isOn: $isPinned) {
                        Label("Anpinnen", systemImage: "pin")
                    }
                } header: {
                    Label("Optionen", systemImage: "gearshape")
                }

                // Reminder Section
                Section {
                    Toggle(isOn: $hasReminder) {
                        Label("Erinnerung", systemImage: "bell")
                    }

                    if hasReminder {
                        DatePicker(
                            "Datum & Zeit",
                            selection: Binding(
                                get: { reminderDate ?? Date() },
                                set: { reminderDate = $0 }
                            ),
                            displayedComponents: [.date, .hourAndMinute]
                        )
                    }
                } header: {
                    Label("Erinnerung", systemImage: "clock")
                }

                // Tags Section
                Section {
                    // Tag Input
                    HStack {
                        TextField("Neuer Tag", text: $newTag)
                            .textInputAutocapitalization(.never)
                            .focused($focusedField, equals: .tag)

                        Button {
                            addTag()
                        } label: {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.blue)
                        }
                        .disabled(newTag.isEmpty)
                    }

                    // Existing Tags
                    if !tags.isEmpty {
                        FlowLayout(spacing: 8) {
                            ForEach(tags, id: \.self) { tag in
                                HStack(spacing: 4) {
                                    Text("#\(tag)")
                                    Button {
                                        removeTag(tag)
                                    } label: {
                                        Image(systemName: "xmark.circle.fill")
                                            .font(.caption)
                                    }
                                }
                                .font(.subheadline)
                                .foregroundColor(.blue)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                } header: {
                    Label("Tags", systemImage: "tag")
                }
            }
            .navigationTitle(mode.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        saveNote()
                    }
                    .fontWeight(.semibold)
                    .disabled(title.isEmpty && content.isEmpty)
                }

                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Fertig") {
                        focusedField = nil
                    }
                }
            }
            .sheet(isPresented: $showingVoiceInput) {
                VoiceInputView { text in
                    switch voiceInputTarget {
                    case .title:
                        title = text
                    case .content:
                        if content.isEmpty {
                            content = text
                        } else {
                            content += "\n" + text
                        }
                    }
                }
            }
        }
    }

    // MARK: - Actions

    private func addTag() {
        let tag = newTag.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if !tag.isEmpty && !tags.contains(tag) {
            tags.append(tag)
            newTag = ""
        }
    }

    private func removeTag(_ tag: String) {
        tags.removeAll { $0 == tag }
    }

    private func saveNote() {
        var note: Note

        switch mode {
        case .create:
            note = Note(
                title: title,
                content: content,
                isPinned: isPinned,
                priority: priority,
                category: category,
                isTodo: isTodo,
                tags: tags,
                reminderDate: hasReminder ? reminderDate : nil
            )
        case .edit(let existingNote):
            note = existingNote
            note.title = title
            note.content = content
            note.isPinned = isPinned
            note.priority = priority
            note.category = category
            note.isTodo = isTodo
            note.tags = tags
            note.reminderDate = hasReminder ? reminderDate : nil
            note.updatedAt = Date()
        }

        onSave(note)
        dismiss()
    }
}

// MARK: - Quick Note Sheet
struct QuickNoteSheet: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var speechService = SpeechRecognitionService()

    @State private var title = ""
    @State private var content = ""
    @State private var isTodo = false

    let onSave: (Note) -> Void

    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                // Title
                TextField("Titel", text: $title)
                    .font(.title2)
                    .padding()
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(12)

                // Content
                TextEditor(text: $content)
                    .frame(minHeight: 100)
                    .padding(8)
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(12)

                // Options
                HStack {
                    Toggle(isOn: $isTodo) {
                        Label("Aufgabe", systemImage: "checklist")
                    }
                    .toggleStyle(.button)

                    Spacer()

                    Button {
                        Task {
                            await speechService.toggleRecording()
                        }
                    } label: {
                        Label(
                            speechService.isRecording ? "Stopp" : "Sprache",
                            systemImage: speechService.isRecording ? "stop.fill" : "mic.fill"
                        )
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(speechService.isRecording ? .red : .blue)
                }

                // Voice Transcription
                if !speechService.transcribedText.isEmpty {
                    Text(speechService.transcribedText)
                        .font(.body)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(12)

                    Button("Text übernehmen") {
                        if content.isEmpty {
                            content = speechService.transcribedText
                        } else {
                            content += "\n" + speechService.transcribedText
                        }
                        speechService.transcribedText = ""
                    }
                    .buttonStyle(.bordered)
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Schnellnotiz")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        let note = Note(
                            title: title.isEmpty ? "Neue Notiz" : title,
                            content: content,
                            isTodo: isTodo
                        )
                        onSave(note)
                        dismiss()
                    }
                    .fontWeight(.semibold)
                    .disabled(title.isEmpty && content.isEmpty)
                }
            }
        }
    }
}

// MARK: - Preview
#Preview("Create") {
    NoteEditorView(mode: .create) { _ in }
}

#Preview("Edit") {
    NoteEditorView(mode: .edit(Note.sampleNotes[0])) { _ in }
}

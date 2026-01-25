import WidgetKit
import SwiftUI

// MARK: - Widget Timeline Provider
struct NotesProvider: TimelineProvider {
    func placeholder(in context: Context) -> NotesEntry {
        NotesEntry(date: Date(), notes: Note.sampleNotes, configuration: .preview)
    }

    func getSnapshot(in context: Context, completion: @escaping (NotesEntry) -> Void) {
        let notes = DataService.loadNotesForWidget()
        let entry = NotesEntry(date: Date(), notes: Array(notes.prefix(5)), configuration: .preview)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<NotesEntry>) -> Void) {
        let notes = DataService.loadNotesForWidget()
        let entry = NotesEntry(date: Date(), notes: Array(notes.prefix(5)), configuration: .preview)

        // Update every 30 minutes
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 30, to: Date())!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }
}

// MARK: - Widget Configuration
struct WidgetConfiguration {
    let showTodosOnly: Bool
    let maxItems: Int

    static let preview = WidgetConfiguration(showTodosOnly: false, maxItems: 5)
}

// MARK: - Timeline Entry
struct NotesEntry: TimelineEntry {
    let date: Date
    let notes: [Note]
    let configuration: WidgetConfiguration
}

// MARK: - Widget Entry View
struct VoiceNotesWidgetEntryView: View {
    var entry: NotesProvider.Entry
    @Environment(\.widgetFamily) var family

    var body: some View {
        switch family {
        case .systemSmall:
            SmallWidgetView(entry: entry)
        case .systemMedium:
            MediumWidgetView(entry: entry)
        case .systemLarge:
            LargeWidgetView(entry: entry)
        case .accessoryCircular:
            AccessoryCircularView(entry: entry)
        case .accessoryRectangular:
            AccessoryRectangularView(entry: entry)
        case .accessoryInline:
            AccessoryInlineView(entry: entry)
        default:
            SmallWidgetView(entry: entry)
        }
    }
}

// MARK: - Small Widget
struct SmallWidgetView: View {
    let entry: NotesEntry

    var todosCount: Int {
        entry.notes.filter { $0.isTodo && !$0.isCompleted }.count
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "note.text")
                    .font(.caption)
                    .foregroundStyle(.blue)
                Text("Voice Notes")
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            // Stats
            VStack(alignment: .leading, spacing: 4) {
                Text("\(entry.notes.count)")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.blue, .purple],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )

                Text("Notizen")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            if todosCount > 0 {
                HStack(spacing: 4) {
                    Image(systemName: "checklist")
                        .font(.caption2)
                    Text("\(todosCount) offen")
                        .font(.caption2)
                }
                .foregroundStyle(.orange)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

// MARK: - Medium Widget
struct MediumWidgetView: View {
    let entry: NotesEntry

    var displayNotes: [Note] {
        Array(entry.notes.prefix(3))
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: "note.text")
                    .foregroundStyle(.blue)
                Text("Voice Notes")
                    .font(.headline)

                Spacer()

                Text("\(entry.notes.count) Notizen")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Divider()

            // Notes List
            if displayNotes.isEmpty {
                Spacer()
                HStack {
                    Spacer()
                    VStack(spacing: 4) {
                        Image(systemName: "note.text.badge.plus")
                            .font(.title2)
                            .foregroundStyle(.secondary)
                        Text("Keine Notizen")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }
                Spacer()
            } else {
                ForEach(displayNotes) { note in
                    WidgetNoteRow(note: note)
                }
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

// MARK: - Large Widget
struct LargeWidgetView: View {
    let entry: NotesEntry

    var displayNotes: [Note] {
        Array(entry.notes.prefix(6))
    }

    var incompleteTodos: [Note] {
        entry.notes.filter { $0.isTodo && !$0.isCompleted }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "note.text")
                        .font(.title3)
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.blue, .purple],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    Text("Voice Notes")
                        .font(.headline)
                }

                Spacer()

                // Quick add button
                Link(destination: URL(string: "voicenotes://new")!) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                        .foregroundStyle(.blue)
                }
            }

            // Stats Row
            HStack(spacing: 16) {
                StatWidget(
                    value: "\(entry.notes.count)",
                    label: "Notizen",
                    icon: "doc.text",
                    color: .blue
                )

                StatWidget(
                    value: "\(incompleteTodos.count)",
                    label: "Offen",
                    icon: "circle",
                    color: .orange
                )

                StatWidget(
                    value: "\(entry.notes.filter { $0.isPinned }.count)",
                    label: "Angepinnt",
                    icon: "pin.fill",
                    color: .purple
                )
            }

            Divider()

            // Notes List
            Text("Neueste Notizen")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundStyle(.secondary)

            if displayNotes.isEmpty {
                Spacer()
                HStack {
                    Spacer()
                    VStack(spacing: 8) {
                        Image(systemName: "note.text.badge.plus")
                            .font(.largeTitle)
                            .foregroundStyle(.secondary)
                        Text("Noch keine Notizen")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        Text("Tippe + um eine zu erstellen")
                            .font(.caption)
                            .foregroundStyle(.tertiary)
                    }
                    Spacer()
                }
                Spacer()
            } else {
                ForEach(displayNotes) { note in
                    WidgetNoteRow(note: note, showCategory: true)
                }
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

// MARK: - Accessory Circular Widget
struct AccessoryCircularView: View {
    let entry: NotesEntry

    var body: some View {
        ZStack {
            AccessoryWidgetBackground()
            VStack(spacing: 2) {
                Image(systemName: "note.text")
                    .font(.caption)
                Text("\(entry.notes.count)")
                    .font(.headline)
            }
        }
    }
}

// MARK: - Accessory Rectangular Widget
struct AccessoryRectangularView: View {
    let entry: NotesEntry

    var latestNote: Note? {
        entry.notes.first
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Image(systemName: "note.text")
                Text("Voice Notes")
                    .fontWeight(.semibold)
            }
            .font(.caption)

            if let note = latestNote {
                Text(note.title)
                    .font(.caption2)
                    .lineLimit(2)
            } else {
                Text("Keine Notizen")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }
}

// MARK: - Accessory Inline Widget
struct AccessoryInlineView: View {
    let entry: NotesEntry

    var openTodos: Int {
        entry.notes.filter { $0.isTodo && !$0.isCompleted }.count
    }

    var body: some View {
        HStack {
            Image(systemName: "checklist")
            Text("\(openTodos) offene Aufgaben")
        }
    }
}

// MARK: - Widget Note Row
struct WidgetNoteRow: View {
    let note: Note
    var showCategory: Bool = false

    var body: some View {
        HStack(spacing: 8) {
            // Checkbox or Category Icon
            if note.isTodo {
                Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.caption)
                    .foregroundStyle(note.isCompleted ? .green : .gray)
            } else if showCategory {
                Image(systemName: note.category.icon)
                    .font(.caption)
                    .foregroundStyle(note.category.color)
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(note.title.isEmpty ? "Ohne Titel" : note.title)
                    .font(.caption)
                    .fontWeight(.medium)
                    .lineLimit(1)
                    .strikethrough(note.isCompleted)
                    .foregroundStyle(note.isCompleted ? .secondary : .primary)

                if !note.content.isEmpty {
                    Text(note.content)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }

            Spacer()

            if note.isPinned {
                Image(systemName: "pin.fill")
                    .font(.caption2)
                    .foregroundStyle(.orange)
            }

            if note.priority == .urgent || note.priority == .high {
                Image(systemName: note.priority.icon)
                    .font(.caption2)
                    .foregroundStyle(note.priority.color)
            }
        }
        .padding(.vertical, 2)
    }
}

// MARK: - Stat Widget
struct StatWidget: View {
    let value: String
    let label: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.caption2)
                Text(value)
                    .font(.headline)
            }
            .foregroundStyle(color)

            Text(label)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

// MARK: - Main Widget
struct VoiceNotesWidget: Widget {
    let kind: String = "VoiceNotesWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: NotesProvider()) { entry in
            VoiceNotesWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Voice Notes")
        .description("Zeige deine Notizen und Aufgaben auf einen Blick.")
        .supportedFamilies([
            .systemSmall,
            .systemMedium,
            .systemLarge,
            .accessoryCircular,
            .accessoryRectangular,
            .accessoryInline
        ])
    }
}

// MARK: - Todo Widget
struct TodoWidget: Widget {
    let kind: String = "TodoWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: TodoProvider()) { entry in
            TodoWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Aufgaben")
        .description("Zeige deine offenen Aufgaben.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

// MARK: - Todo Provider
struct TodoProvider: TimelineProvider {
    func placeholder(in context: Context) -> TodoEntry {
        TodoEntry(date: Date(), todos: Note.sampleNotes.filter { $0.isTodo })
    }

    func getSnapshot(in context: Context, completion: @escaping (TodoEntry) -> Void) {
        let notes = DataService.loadNotesForWidget()
        let todos = notes.filter { $0.isTodo && !$0.isCompleted }
        completion(TodoEntry(date: Date(), todos: Array(todos.prefix(5))))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<TodoEntry>) -> Void) {
        let notes = DataService.loadNotesForWidget()
        let todos = notes.filter { $0.isTodo && !$0.isCompleted }
        let entry = TodoEntry(date: Date(), todos: Array(todos.prefix(5)))

        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 15, to: Date())!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }
}

struct TodoEntry: TimelineEntry {
    let date: Date
    let todos: [Note]
}

struct TodoWidgetEntryView: View {
    var entry: TodoEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        switch family {
        case .systemSmall:
            SmallTodoWidget(entry: entry)
        case .systemMedium:
            MediumTodoWidget(entry: entry)
        default:
            SmallTodoWidget(entry: entry)
        }
    }
}

struct SmallTodoWidget: View {
    let entry: TodoEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "checklist")
                    .foregroundStyle(.green)
                Text("Aufgaben")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Text("\(entry.todos.count)")
                .font(.system(size: 42, weight: .bold, design: .rounded))
                .foregroundStyle(.green)

            Text("offen")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

struct MediumTodoWidget: View {
    let entry: TodoEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "checklist")
                    .foregroundStyle(.green)
                Text("Offene Aufgaben")
                    .font(.headline)

                Spacer()

                Link(destination: URL(string: "voicenotes://todo")!) {
                    Image(systemName: "plus.circle.fill")
                        .foregroundStyle(.green)
                }
            }

            Divider()

            if entry.todos.isEmpty {
                Spacer()
                HStack {
                    Spacer()
                    VStack(spacing: 4) {
                        Image(systemName: "checkmark.circle")
                            .font(.title)
                            .foregroundStyle(.green)
                        Text("Alles erledigt!")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }
                Spacer()
            } else {
                ForEach(entry.todos.prefix(3)) { todo in
                    WidgetNoteRow(note: todo)
                }
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        .padding()
        .containerBackground(.fill.tertiary, for: .widget)
    }
}

// MARK: - Preview
#Preview("Small", as: .systemSmall) {
    VoiceNotesWidget()
} timeline: {
    NotesEntry(date: Date(), notes: Note.sampleNotes, configuration: .preview)
}

#Preview("Medium", as: .systemMedium) {
    VoiceNotesWidget()
} timeline: {
    NotesEntry(date: Date(), notes: Note.sampleNotes, configuration: .preview)
}

#Preview("Large", as: .systemLarge) {
    VoiceNotesWidget()
} timeline: {
    NotesEntry(date: Date(), notes: Note.sampleNotes, configuration: .preview)
}

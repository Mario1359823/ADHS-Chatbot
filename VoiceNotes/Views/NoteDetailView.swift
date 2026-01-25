import SwiftUI

// MARK: - Note Detail View
struct NoteDetailView: View {
    @State var note: Note
    @ObservedObject var viewModel: NotesViewModel
    @Environment(\.dismiss) private var dismiss

    @State private var isEditing = false
    @State private var showingDeleteAlert = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header Card
                    headerCard

                    // Content
                    contentSection

                    // Tags
                    if !note.tags.isEmpty {
                        tagsSection
                    }

                    // Meta Info
                    metaInfoSection

                    // Quick Actions
                    quickActionsSection
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Schließen") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            isEditing = true
                        } label: {
                            Label("Bearbeiten", systemImage: "pencil")
                        }

                        Button {
                            viewModel.togglePinned(note)
                            note.isPinned.toggle()
                        } label: {
                            Label(note.isPinned ? "Lösen" : "Anpinnen", systemImage: note.isPinned ? "pin.slash" : "pin")
                        }

                        Divider()

                        Button(role: .destructive) {
                            showingDeleteAlert = true
                        } label: {
                            Label("Löschen", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(isPresented: $isEditing) {
                NoteEditorView(mode: .edit(note)) { updatedNote in
                    viewModel.updateNote(updatedNote)
                    note = updatedNote
                }
            }
            .alert("Notiz löschen?", isPresented: $showingDeleteAlert) {
                Button("Abbrechen", role: .cancel) {}
                Button("Löschen", role: .destructive) {
                    viewModel.deleteNote(note)
                    dismiss()
                }
            } message: {
                Text("Diese Aktion kann nicht rückgängig gemacht werden.")
            }
        }
    }

    // MARK: - Header Card
    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                // Category Badge
                HStack(spacing: 6) {
                    Image(systemName: note.category.icon)
                    Text(note.category.rawValue)
                }
                .font(.caption)
                .foregroundColor(.white)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(note.category.color)
                .cornerRadius(8)

                // Priority Badge
                if note.priority != .normal {
                    HStack(spacing: 4) {
                        Image(systemName: note.priority.icon)
                        Text(note.priority.rawValue)
                    }
                    .font(.caption)
                    .foregroundColor(note.priority.color)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(note.priority.color.opacity(0.15))
                    .cornerRadius(8)
                }

                Spacer()

                // Pinned Badge
                if note.isPinned {
                    Image(systemName: "pin.fill")
                        .foregroundColor(.orange)
                }
            }

            // Title
            Text(note.title.isEmpty ? "Ohne Titel" : note.title)
                .font(.title2)
                .fontWeight(.bold)
                .strikethrough(note.isCompleted)
                .foregroundColor(note.isCompleted ? .secondary : .primary)

            // Todo Status
            if note.isTodo {
                HStack {
                    Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                        .foregroundColor(note.isCompleted ? .green : .gray)
                    Text(note.isCompleted ? "Erledigt" : "Offen")
                        .foregroundColor(note.isCompleted ? .green : .primary)
                }
                .font(.subheadline)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }

    // MARK: - Content Section
    private var contentSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Inhalt", systemImage: "doc.text")
                .font(.headline)
                .foregroundColor(.secondary)

            Text(note.content.isEmpty ? "Kein Inhalt" : note.content)
                .font(.body)
                .foregroundColor(note.content.isEmpty ? .secondary : .primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(Color(.secondarySystemBackground))
                .cornerRadius(12)
        }
    }

    // MARK: - Tags Section
    private var tagsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Tags", systemImage: "tag")
                .font(.headline)
                .foregroundColor(.secondary)

            FlowLayout(spacing: 8) {
                ForEach(note.tags, id: \.self) { tag in
                    Text("#\(tag)")
                        .font(.subheadline)
                        .foregroundColor(.blue)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                }
            }
        }
    }

    // MARK: - Meta Info Section
    private var metaInfoSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Information", systemImage: "info.circle")
                .font(.headline)
                .foregroundColor(.secondary)

            VStack(spacing: 0) {
                MetaInfoRow(icon: "calendar.badge.plus", title: "Erstellt", value: note.createdAt.formatted(date: .long, time: .shortened))

                Divider()

                MetaInfoRow(icon: "calendar.badge.clock", title: "Bearbeitet", value: note.updatedAt.formatted(date: .long, time: .shortened))

                if let reminder = note.reminderDate {
                    Divider()
                    MetaInfoRow(icon: "bell", title: "Erinnerung", value: reminder.formatted(date: .long, time: .shortened))
                }
            }
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
        }
    }

    // MARK: - Quick Actions Section
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Aktionen", systemImage: "bolt")
                .font(.headline)
                .foregroundColor(.secondary)

            HStack(spacing: 12) {
                // Edit
                QuickActionButton(icon: "pencil", title: "Bearbeiten", color: .blue) {
                    isEditing = true
                }

                // Toggle Pin
                QuickActionButton(
                    icon: note.isPinned ? "pin.slash" : "pin",
                    title: note.isPinned ? "Lösen" : "Anpinnen",
                    color: .orange
                ) {
                    viewModel.togglePinned(note)
                    note.isPinned.toggle()
                }

                // Toggle Complete (if todo)
                if note.isTodo {
                    QuickActionButton(
                        icon: note.isCompleted ? "arrow.uturn.backward" : "checkmark",
                        title: note.isCompleted ? "Öffnen" : "Erledigen",
                        color: .green
                    ) {
                        viewModel.toggleCompleted(note)
                        note.isCompleted.toggle()
                    }
                }

                // Share
                QuickActionButton(icon: "square.and.arrow.up", title: "Teilen", color: .purple) {
                    shareNote()
                }
            }
        }
    }

    private func shareNote() {
        let text = """
        \(note.title)

        \(note.content)

        Tags: \(note.tags.map { "#\($0)" }.joined(separator: " "))
        """

        let activityController = UIActivityViewController(activityItems: [text], applicationActivities: nil)

        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first,
           let rootVC = window.rootViewController {
            rootVC.present(activityController, animated: true)
        }
    }
}

// MARK: - Meta Info Row
struct MetaInfoRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.secondary)
                .frame(width: 24)

            Text(title)
                .foregroundColor(.secondary)

            Spacer()

            Text(value)
                .foregroundColor(.primary)
        }
        .padding()
    }
}

// MARK: - Quick Action Button
struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(color)
                    .clipShape(Circle())

                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Flow Layout for Tags
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(in: proposal.width ?? 0, subviews: subviews, spacing: spacing)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(in: bounds.width, subviews: subviews, spacing: spacing)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x, y: bounds.minY + result.positions[index].y), proposal: .unspecified)
        }
    }

    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []

        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var x: CGFloat = 0
            var y: CGFloat = 0
            var rowHeight: CGFloat = 0

            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)

                if x + size.width > maxWidth && x > 0 {
                    x = 0
                    y += rowHeight + spacing
                    rowHeight = 0
                }

                positions.append(CGPoint(x: x, y: y))
                rowHeight = max(rowHeight, size.height)
                x += size.width + spacing
            }

            self.size = CGSize(width: maxWidth, height: y + rowHeight)
        }
    }
}

// MARK: - Preview
#Preview {
    NoteDetailView(
        note: Note.sampleNotes[0],
        viewModel: NotesViewModel()
    )
}

import SwiftUI

// MARK: - Note Card View
struct NoteCardView: View {
    let note: Note
    let onToggleComplete: () -> Void
    let onTogglePin: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                // Category Icon
                Image(systemName: note.category.icon)
                    .font(.caption)
                    .foregroundColor(note.category.color)
                    .padding(6)
                    .background(note.category.color.opacity(0.15))
                    .clipShape(Circle())

                VStack(alignment: .leading, spacing: 2) {
                    Text(note.title.isEmpty ? "Ohne Titel" : note.title)
                        .font(.headline)
                        .lineLimit(1)
                        .strikethrough(note.isCompleted)
                        .foregroundColor(note.isCompleted ? .secondary : .primary)

                    Text(note.updatedAt.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                // Priority Badge
                if note.priority != .normal {
                    Image(systemName: note.priority.icon)
                        .font(.caption)
                        .foregroundColor(note.priority.color)
                }

                // Pin Button
                if note.isPinned {
                    Image(systemName: "pin.fill")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
            }

            // Content Preview
            if !note.content.isEmpty {
                Text(note.content)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }

            // Footer
            HStack {
                // Tags
                if !note.tags.isEmpty {
                    HStack(spacing: 4) {
                        ForEach(note.tags.prefix(3), id: \.self) { tag in
                            Text("#\(tag)")
                                .font(.caption2)
                                .foregroundColor(.blue)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(4)
                        }
                    }
                }

                Spacer()

                // Todo Checkbox
                if note.isTodo {
                    Button(action: onToggleComplete) {
                        Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                            .font(.title3)
                            .foregroundColor(note.isCompleted ? .green : .gray)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }

    private var cardBackground: some View {
        Group {
            if note.isCompleted {
                Color(.secondarySystemBackground).opacity(0.7)
            } else {
                Color(.secondarySystemBackground)
            }
        }
    }
}

// MARK: - Compact Note Card
struct CompactNoteCard: View {
    let note: Note

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
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .lineLimit(1)

                    if note.isPinned {
                        Image(systemName: "pin.fill")
                            .font(.caption2)
                            .foregroundColor(.orange)
                    }
                }

                Text(note.content)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }

            Spacer()

            if note.isTodo {
                Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(note.isCompleted ? .green : .gray)
            }
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Note Grid Card (for grid layout)
struct NoteGridCard: View {
    let note: Note
    let onToggleComplete: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Image(systemName: note.category.icon)
                    .font(.caption)
                    .foregroundColor(note.category.color)

                Spacer()

                if note.isPinned {
                    Image(systemName: "pin.fill")
                        .font(.caption)
                        .foregroundColor(.orange)
                }

                if note.priority != .normal {
                    Image(systemName: note.priority.icon)
                        .font(.caption)
                        .foregroundColor(note.priority.color)
                }
            }

            // Title
            Text(note.title.isEmpty ? "Ohne Titel" : note.title)
                .font(.headline)
                .lineLimit(2)
                .strikethrough(note.isCompleted)

            // Content
            Text(note.content)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(4)

            Spacer()

            // Footer
            HStack {
                Text(note.updatedAt.formatted(date: .abbreviated, time: .omitted))
                    .font(.caption2)
                    .foregroundColor(.secondary)

                Spacer()

                if note.isTodo {
                    Button(action: onToggleComplete) {
                        Image(systemName: note.isCompleted ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(note.isCompleted ? .green : .gray)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding()
        .frame(minHeight: 150)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Preview
#Preview {
    VStack(spacing: 16) {
        NoteCardView(
            note: Note.sampleNotes[0],
            onToggleComplete: {},
            onTogglePin: {}
        )

        CompactNoteCard(note: Note.sampleNotes[1])

        NoteGridCard(
            note: Note.sampleNotes[2],
            onToggleComplete: {}
        )
        .frame(width: 180)
    }
    .padding()
}

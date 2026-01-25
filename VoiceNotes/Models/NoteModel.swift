import Foundation
import SwiftUI

// MARK: - Note Model
struct Note: Identifiable, Codable, Hashable {
    var id: UUID
    var title: String
    var content: String
    var createdAt: Date
    var updatedAt: Date
    var isPinned: Bool
    var priority: Priority
    var category: Category
    var isTodo: Bool
    var isCompleted: Bool
    var tags: [String]
    var reminderDate: Date?

    init(
        id: UUID = UUID(),
        title: String = "",
        content: String = "",
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        isPinned: Bool = false,
        priority: Priority = .normal,
        category: Category = .personal,
        isTodo: Bool = false,
        isCompleted: Bool = false,
        tags: [String] = [],
        reminderDate: Date? = nil
    ) {
        self.id = id
        self.title = title
        self.content = content
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.isPinned = isPinned
        self.priority = priority
        self.category = category
        self.isTodo = isTodo
        self.isCompleted = isCompleted
        self.tags = tags
        self.reminderDate = reminderDate
    }
}

// MARK: - Priority Enum
enum Priority: String, Codable, CaseIterable {
    case low = "Niedrig"
    case normal = "Normal"
    case high = "Hoch"
    case urgent = "Dringend"

    var color: Color {
        switch self {
        case .low: return .gray
        case .normal: return .blue
        case .high: return .orange
        case .urgent: return .red
        }
    }

    var icon: String {
        switch self {
        case .low: return "arrow.down.circle"
        case .normal: return "minus.circle"
        case .high: return "arrow.up.circle"
        case .urgent: return "exclamationmark.circle.fill"
        }
    }
}

// MARK: - Category Enum
enum Category: String, Codable, CaseIterable {
    case personal = "Persönlich"
    case work = "Arbeit"
    case shopping = "Einkaufen"
    case health = "Gesundheit"
    case ideas = "Ideen"
    case other = "Sonstiges"

    var color: Color {
        switch self {
        case .personal: return .purple
        case .work: return .blue
        case .shopping: return .green
        case .health: return .red
        case .ideas: return .yellow
        case .other: return .gray
        }
    }

    var icon: String {
        switch self {
        case .personal: return "person.fill"
        case .work: return "briefcase.fill"
        case .shopping: return "cart.fill"
        case .health: return "heart.fill"
        case .ideas: return "lightbulb.fill"
        case .other: return "folder.fill"
        }
    }
}

// MARK: - Sample Data
extension Note {
    static let sampleNotes: [Note] = [
        Note(
            title: "Einkaufsliste",
            content: "- Milch\n- Brot\n- Eier\n- Käse\n- Obst",
            isPinned: true,
            priority: .normal,
            category: .shopping,
            isTodo: true,
            tags: ["einkaufen", "wichtig"]
        ),
        Note(
            title: "Meeting Notizen",
            content: "Projekt Update besprechen\nDeadline: nächste Woche\nTeam informieren",
            priority: .high,
            category: .work,
            tags: ["arbeit", "meeting"]
        ),
        Note(
            title: "Trainingsplan",
            content: "Mo: Joggen\nMi: Krafttraining\nFr: Schwimmen",
            priority: .normal,
            category: .health,
            isTodo: true,
            tags: ["fitness", "gesundheit"]
        ),
        Note(
            title: "App Idee",
            content: "Eine App die Notizen per Sprache aufnimmt und automatisch kategorisiert.",
            priority: .low,
            category: .ideas,
            tags: ["idee", "app"]
        )
    ]
}

// ===== Voice Notes App =====

// Category & Priority Configuration
const CATEGORIES = {
    personal: { name: 'Persönlich', icon: '👤', color: '#AF52DE' },
    work: { name: 'Arbeit', icon: '💼', color: '#007AFF' },
    shopping: { name: 'Einkaufen', icon: '🛒', color: '#34C759' },
    health: { name: 'Gesundheit', icon: '❤️', color: '#FF3B30' },
    ideas: { name: 'Ideen', icon: '💡', color: '#FFCC00' },
    other: { name: 'Sonstiges', icon: '📁', color: '#8E8E93' }
};

const PRIORITIES = {
    low: { name: 'Niedrig', color: '#8E8E93' },
    normal: { name: 'Normal', color: '#007AFF' },
    high: { name: 'Hoch', color: '#FF9500' },
    urgent: { name: 'Dringend', color: '#FF3B30' }
};

// ===== State Management =====
let notes = [];
let currentTab = 'all';
let currentEditId = null;
let searchQuery = '';
let categoryFilter = '';
let priorityFilter = '';

// ===== DOM Elements =====
const elements = {
    notesList: document.getElementById('notesList'),
    emptyState: document.getElementById('emptyState'),
    totalCount: document.getElementById('totalCount'),
    todoCount: document.getElementById('todoCount'),
    completionRate: document.getElementById('completionRate'),
    searchBar: document.getElementById('searchBar'),
    searchInput: document.getElementById('searchInput'),
    searchToggle: document.getElementById('searchToggle'),
    clearSearch: document.getElementById('clearSearch'),
    filterBar: document.getElementById('filterBar'),
    filterToggle: document.getElementById('filterToggle'),
    categoryFilter: document.getElementById('categoryFilter'),
    priorityFilter: document.getElementById('priorityFilter'),
    tabs: document.querySelectorAll('.tab'),
    editorModal: document.getElementById('editorModal'),
    editorTitle: document.getElementById('editorTitle'),
    noteTitle: document.getElementById('noteTitle'),
    noteContent: document.getElementById('noteContent'),
    noteCategory: document.getElementById('noteCategory'),
    notePriority: document.getElementById('notePriority'),
    noteTodo: document.getElementById('noteTodo'),
    notePinned: document.getElementById('notePinned'),
    noteTags: document.getElementById('noteTags'),
    voiceModal: document.getElementById('voiceModal'),
    voiceInstructions: document.getElementById('voiceInstructions'),
    voiceWaveform: document.getElementById('voiceWaveform'),
    transcriptContainer: document.getElementById('transcriptContainer'),
    transcript: document.getElementById('transcript'),
    recordBtn: document.getElementById('recordBtn'),
    voiceOptions: document.getElementById('voiceOptions'),
    detailModal: document.getElementById('detailModal'),
    detailContent: document.getElementById('detailContent'),
    toast: document.getElementById('toast')
};

// ===== Initialize =====
function init() {
    loadNotes();
    renderNotes();
    updateStats();
    setupEventListeners();
    registerServiceWorker();
}

// ===== Local Storage =====
function loadNotes() {
    const saved = localStorage.getItem('voiceNotes');
    if (saved) {
        notes = JSON.parse(saved);
    } else {
        // Sample notes for first load
        notes = [
            {
                id: generateId(),
                title: 'Willkommen bei Voice Notes!',
                content: 'Dies ist deine erste Notiz. Du kannst:\n- Neue Notizen erstellen\n- Per Sprache diktieren\n- Aufgaben abhaken',
                category: 'ideas',
                priority: 'normal',
                isTodo: false,
                isCompleted: false,
                isPinned: true,
                tags: ['willkommen'],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            },
            {
                id: generateId(),
                title: 'Einkaufsliste',
                content: '- Milch\n- Brot\n- Eier\n- Käse',
                category: 'shopping',
                priority: 'normal',
                isTodo: true,
                isCompleted: false,
                isPinned: false,
                tags: ['einkaufen'],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            }
        ];
        saveNotes();
    }
}

function saveNotes() {
    localStorage.setItem('voiceNotes', JSON.stringify(notes));
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// ===== Render Functions =====
function renderNotes() {
    let filtered = getFilteredNotes();

    if (filtered.length === 0) {
        elements.notesList.classList.add('hidden');
        elements.emptyState.classList.remove('hidden');
        return;
    }

    elements.notesList.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');

    // Sort: pinned first, then by date
    filtered.sort((a, b) => {
        if (a.isPinned && !b.isPinned) return -1;
        if (!a.isPinned && b.isPinned) return 1;
        return new Date(b.updatedAt) - new Date(a.updatedAt);
    });

    elements.notesList.innerHTML = filtered.map(note => createNoteCard(note)).join('');

    // Add event listeners to cards
    elements.notesList.querySelectorAll('.note-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.todo-checkbox')) {
                openDetailModal(card.dataset.id);
            }
        });
    });

    // Add event listeners to checkboxes
    elements.notesList.querySelectorAll('.todo-checkbox').forEach(checkbox => {
        checkbox.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleComplete(checkbox.dataset.id);
        });
    });
}

function createNoteCard(note) {
    const cat = CATEGORIES[note.category];
    const prio = PRIORITIES[note.priority];

    const badges = [];
    if (note.isPinned) badges.push('<span class="badge pinned">📌</span>');
    if (note.priority === 'urgent') badges.push('<span class="badge priority-urgent">🔴</span>');
    else if (note.priority === 'high') badges.push('<span class="badge priority-high">🟠</span>');

    const tagsHtml = note.tags.slice(0, 3).map(tag =>
        `<span class="tag">#${tag}</span>`
    ).join('');

    const checkboxHtml = note.isTodo ? `
        <div class="todo-checkbox ${note.isCompleted ? 'checked' : ''}" data-id="${note.id}">
            ${note.isCompleted ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 13l4 4L19 7"/></svg>' : ''}
        </div>
    ` : '';

    return `
        <div class="note-card ${note.isCompleted ? 'completed' : ''}" data-id="${note.id}">
            <div class="note-card-header">
                <div class="category-icon ${note.category}">${cat.icon}</div>
                <div class="note-info">
                    <div class="note-title">${escapeHtml(note.title) || 'Ohne Titel'}</div>
                    <div class="note-meta">
                        <span>${formatDate(note.updatedAt)}</span>
                        <div class="note-badges">${badges.join('')}</div>
                    </div>
                </div>
            </div>
            ${note.content ? `<div class="note-content">${escapeHtml(note.content)}</div>` : ''}
            <div class="note-footer">
                <div class="note-tags">${tagsHtml}</div>
                ${checkboxHtml}
            </div>
        </div>
    `;
}

function getFilteredNotes() {
    let filtered = [...notes];

    // Tab filter
    switch (currentTab) {
        case 'notes':
            filtered = filtered.filter(n => !n.isTodo);
            break;
        case 'todos':
            filtered = filtered.filter(n => n.isTodo);
            break;
        case 'pinned':
            filtered = filtered.filter(n => n.isPinned);
            break;
    }

    // Search filter
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(n =>
            n.title.toLowerCase().includes(query) ||
            n.content.toLowerCase().includes(query) ||
            n.tags.some(t => t.toLowerCase().includes(query))
        );
    }

    // Category filter
    if (categoryFilter) {
        filtered = filtered.filter(n => n.category === categoryFilter);
    }

    // Priority filter
    if (priorityFilter) {
        filtered = filtered.filter(n => n.priority === priorityFilter);
    }

    return filtered;
}

function updateStats() {
    const total = notes.length;
    const todos = notes.filter(n => n.isTodo);
    const completed = todos.filter(n => n.isCompleted).length;
    const rate = todos.length > 0 ? Math.round((completed / todos.length) * 100) : 0;

    elements.totalCount.textContent = total;
    elements.todoCount.textContent = `${completed}/${todos.length}`;
    elements.completionRate.textContent = `${rate}%`;
}

// ===== CRUD Operations =====
function addNote(noteData) {
    const note = {
        id: generateId(),
        title: noteData.title || '',
        content: noteData.content || '',
        category: noteData.category || 'personal',
        priority: noteData.priority || 'normal',
        isTodo: noteData.isTodo || false,
        isCompleted: false,
        isPinned: noteData.isPinned || false,
        tags: noteData.tags || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    notes.unshift(note);
    saveNotes();
    renderNotes();
    updateStats();
    showToast('Notiz erstellt');
    return note;
}

function updateNote(id, updates) {
    const index = notes.findIndex(n => n.id === id);
    if (index !== -1) {
        notes[index] = {
            ...notes[index],
            ...updates,
            updatedAt: new Date().toISOString()
        };
        saveNotes();
        renderNotes();
        updateStats();
        showToast('Notiz aktualisiert');
    }
}

function deleteNote(id) {
    notes = notes.filter(n => n.id !== id);
    saveNotes();
    renderNotes();
    updateStats();
    showToast('Notiz gelöscht');
}

function toggleComplete(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        note.isCompleted = !note.isCompleted;
        note.updatedAt = new Date().toISOString();
        saveNotes();
        renderNotes();
        updateStats();

        if (note.isCompleted) {
            showToast('Aufgabe erledigt ✓');
        }
    }
}

function togglePin(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        note.isPinned = !note.isPinned;
        note.updatedAt = new Date().toISOString();
        saveNotes();
        renderNotes();
        showToast(note.isPinned ? 'Angepinnt' : 'Gelöst');
    }
}

// ===== Modal Functions =====
function openEditorModal(noteId = null) {
    currentEditId = noteId;

    if (noteId) {
        const note = notes.find(n => n.id === noteId);
        if (!note) return;

        elements.editorTitle.textContent = 'Bearbeiten';
        elements.noteTitle.value = note.title;
        elements.noteContent.value = note.content;
        elements.noteCategory.value = note.category;
        elements.notePriority.value = note.priority;
        elements.noteTodo.checked = note.isTodo;
        elements.notePinned.checked = note.isPinned;
        elements.noteTags.value = note.tags.join(', ');
    } else {
        elements.editorTitle.textContent = 'Neue Notiz';
        elements.noteTitle.value = '';
        elements.noteContent.value = '';
        elements.noteCategory.value = 'personal';
        elements.notePriority.value = 'normal';
        elements.noteTodo.checked = false;
        elements.notePinned.checked = false;
        elements.noteTags.value = '';
    }

    showModal(elements.editorModal);
    elements.noteTitle.focus();
}

function closeEditorModal() {
    hideModal(elements.editorModal);
    currentEditId = null;
}

function saveCurrentNote() {
    const title = elements.noteTitle.value.trim();
    const content = elements.noteContent.value.trim();

    if (!title && !content) {
        showToast('Bitte Titel oder Inhalt eingeben');
        return;
    }

    const tags = elements.noteTags.value
        .split(',')
        .map(t => t.trim().toLowerCase())
        .filter(t => t);

    const noteData = {
        title,
        content,
        category: elements.noteCategory.value,
        priority: elements.notePriority.value,
        isTodo: elements.noteTodo.checked,
        isPinned: elements.notePinned.checked,
        tags
    };

    if (currentEditId) {
        updateNote(currentEditId, noteData);
    } else {
        addNote(noteData);
    }

    closeEditorModal();
}

function openDetailModal(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (!note) return;

    currentEditId = noteId;
    const cat = CATEGORIES[note.category];
    const prio = PRIORITIES[note.priority];

    elements.detailContent.innerHTML = `
        <div class="detail-header">
            <div class="category-icon ${note.category}">${cat.icon}</div>
            <div class="detail-info">
                <h1 class="detail-title">${escapeHtml(note.title) || 'Ohne Titel'}</h1>
                <div class="detail-badges">
                    <span class="detail-badge category" style="background: ${cat.color}">${cat.name}</span>
                    <span class="detail-badge priority" style="color: ${prio.color}">${prio.name}</span>
                    ${note.isTodo ? '<span class="detail-badge" style="background: #34C759; color: white">Aufgabe</span>' : ''}
                    ${note.isPinned ? '<span class="detail-badge" style="background: #FF9500; color: white">📌 Angepinnt</span>' : ''}
                </div>
            </div>
        </div>

        <div class="detail-section">
            <div class="detail-section-title">Inhalt</div>
            <div class="detail-content">${escapeHtml(note.content) || 'Kein Inhalt'}</div>
        </div>

        ${note.tags.length > 0 ? `
            <div class="detail-section">
                <div class="detail-section-title">Tags</div>
                <div class="note-tags" style="padding: 12px; background: var(--bg-secondary); border-radius: 12px;">
                    ${note.tags.map(tag => `<span class="tag">#${tag}</span>`).join('')}
                </div>
            </div>
        ` : ''}

        <div class="detail-section">
            <div class="detail-section-title">Information</div>
            <div class="detail-meta">
                <div class="meta-row">
                    <span class="meta-label">Erstellt</span>
                    <span>${formatDateTime(note.createdAt)}</span>
                </div>
                <div class="meta-row">
                    <span class="meta-label">Bearbeitet</span>
                    <span>${formatDateTime(note.updatedAt)}</span>
                </div>
            </div>
        </div>

        <div class="detail-actions">
            <button class="action-btn pin" onclick="togglePin('${note.id}'); closeDetailModal();">
                ${note.isPinned ? '📌 Lösen' : '📌 Anpinnen'}
            </button>
            ${note.isTodo ? `
                <button class="action-btn complete" onclick="toggleComplete('${note.id}'); closeDetailModal();">
                    ${note.isCompleted ? '↩️ Öffnen' : '✓ Erledigen'}
                </button>
            ` : ''}
            <button class="action-btn delete" onclick="if(confirm('Notiz löschen?')) { deleteNote('${note.id}'); closeDetailModal(); }">
                🗑️ Löschen
            </button>
        </div>
    `;

    showModal(elements.detailModal);
}

function closeDetailModal() {
    hideModal(elements.detailModal);
    currentEditId = null;
}

function showModal(modal) {
    modal.classList.remove('hidden');
    requestAnimationFrame(() => {
        modal.classList.add('visible');
    });
}

function hideModal(modal) {
    modal.classList.remove('visible');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

// ===== Voice Recognition =====
let recognition = null;
let isRecording = false;
let finalTranscript = '';

function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Spracherkennung nicht unterstützt');
        return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'de-DE';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
        isRecording = true;
        elements.recordBtn.classList.add('recording');
        elements.voiceInstructions.textContent = 'Sprich jetzt...';
        elements.voiceWaveform.classList.remove('hidden');
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        elements.transcript.textContent = finalTranscript + interimTranscript;
        elements.transcriptContainer.classList.remove('hidden');

        if (finalTranscript.trim()) {
            document.getElementById('saveVoice').disabled = false;
            elements.voiceOptions.classList.remove('hidden');
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'not-allowed') {
            showToast('Mikrofon-Zugriff verweigert');
        } else {
            showToast('Fehler bei der Spracherkennung');
        }
        stopRecording();
    };

    recognition.onend = () => {
        isRecording = false;
        elements.recordBtn.classList.remove('recording');
        elements.voiceWaveform.classList.add('hidden');
        elements.voiceInstructions.textContent = 'Tippe zum Starten';
    };

    return true;
}

function startRecording() {
    if (!recognition && !initSpeechRecognition()) return;

    finalTranscript = '';
    elements.transcript.textContent = '';
    elements.transcriptContainer.classList.add('hidden');
    elements.voiceOptions.classList.add('hidden');
    document.getElementById('saveVoice').disabled = true;

    try {
        recognition.start();
    } catch (e) {
        console.error('Could not start recognition:', e);
    }
}

function stopRecording() {
    if (recognition) {
        recognition.stop();
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function openVoiceModal() {
    showModal(elements.voiceModal);
    finalTranscript = '';
    elements.transcript.textContent = '';
    elements.transcriptContainer.classList.add('hidden');
    elements.voiceOptions.classList.add('hidden');
    document.getElementById('saveVoice').disabled = true;
    elements.voiceInstructions.textContent = 'Tippe zum Starten';
}

function closeVoiceModal() {
    stopRecording();
    hideModal(elements.voiceModal);
}

function saveVoiceNote(asTodo = false) {
    const text = finalTranscript.trim();
    if (!text) return;

    // First line as title, rest as content
    const lines = text.split(/[.!?]\s*/);
    const title = lines[0] || 'Sprachnotiz';
    const content = lines.slice(1).join('. ') || text;

    addNote({
        title: title.substring(0, 100),
        content: content,
        isTodo: asTodo,
        tags: ['sprachnotiz']
    });

    closeVoiceModal();
}

// Voice input in editor
function startEditorVoiceInput() {
    if (!recognition && !initSpeechRecognition()) return;

    const originalOnResult = recognition.onresult;

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                elements.noteContent.value += transcript + ' ';
            }
        }
    };

    recognition.onend = () => {
        isRecording = false;
        document.getElementById('voiceInputBtn').style.background = 'var(--primary)';
        recognition.onresult = originalOnResult;
    };

    if (isRecording) {
        stopRecording();
        document.getElementById('voiceInputBtn').style.background = 'var(--primary)';
    } else {
        recognition.start();
        document.getElementById('voiceInputBtn').style.background = 'var(--danger)';
    }
}

// ===== Event Listeners =====
function setupEventListeners() {
    // FAB Buttons
    document.getElementById('addBtn').addEventListener('click', () => openEditorModal());
    document.getElementById('voiceBtn').addEventListener('click', openVoiceModal);

    // Editor Modal
    document.getElementById('cancelEdit').addEventListener('click', closeEditorModal);
    document.getElementById('saveNote').addEventListener('click', saveCurrentNote);
    document.getElementById('voiceInputBtn').addEventListener('click', startEditorVoiceInput);

    // Voice Modal
    document.getElementById('cancelVoice').addEventListener('click', closeVoiceModal);
    document.getElementById('saveVoice').addEventListener('click', () => saveVoiceNote(false));
    elements.recordBtn.addEventListener('click', toggleRecording);

    // Voice options
    elements.voiceOptions.querySelectorAll('.voice-option-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            saveVoiceNote(btn.dataset.type === 'todo');
        });
    });

    // Detail Modal
    document.getElementById('closeDetail').addEventListener('click', closeDetailModal);
    document.getElementById('editNote').addEventListener('click', () => {
        closeDetailModal();
        setTimeout(() => openEditorModal(currentEditId), 300);
    });

    // Search
    elements.searchToggle.addEventListener('click', () => {
        elements.searchBar.classList.toggle('hidden');
        if (!elements.searchBar.classList.contains('hidden')) {
            elements.searchInput.focus();
        }
    });

    elements.searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderNotes();
    });

    elements.clearSearch.addEventListener('click', () => {
        searchQuery = '';
        elements.searchInput.value = '';
        renderNotes();
    });

    // Filters
    elements.filterToggle.addEventListener('click', () => {
        elements.filterBar.classList.toggle('hidden');
    });

    elements.categoryFilter.addEventListener('change', (e) => {
        categoryFilter = e.target.value;
        renderNotes();
    });

    elements.priorityFilter.addEventListener('change', (e) => {
        priorityFilter = e.target.value;
        renderNotes();
    });

    // Tabs
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            renderNotes();
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (!elements.editorModal.classList.contains('hidden')) closeEditorModal();
            if (!elements.voiceModal.classList.contains('hidden')) closeVoiceModal();
            if (!elements.detailModal.classList.contains('hidden')) closeDetailModal();
        }
    });
}

// ===== Utility Functions =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
        return 'Heute, ' + date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
        return 'Gestern';
    } else if (days < 7) {
        return date.toLocaleDateString('de-DE', { weekday: 'long' });
    } else {
        return date.toLocaleDateString('de-DE', { day: 'numeric', month: 'short' });
    }
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleDateString('de-DE', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showToast(message) {
    elements.toast.textContent = message;
    elements.toast.classList.remove('hidden');
    requestAnimationFrame(() => {
        elements.toast.classList.add('visible');
    });

    setTimeout(() => {
        elements.toast.classList.remove('visible');
        setTimeout(() => {
            elements.toast.classList.add('hidden');
        }, 300);
    }, 2000);
}

// ===== Service Worker =====
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    }
}

// ===== Start App =====
document.addEventListener('DOMContentLoaded', init);

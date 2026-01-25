import SwiftUI

// MARK: - Voice Input View
struct VoiceInputView: View {
    @StateObject private var speechService = SpeechRecognitionService()
    @Environment(\.dismiss) private var dismiss

    var onSave: (String) -> Void

    @State private var showingSaveOptions = false

    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Instructions
                if speechService.transcribedText.isEmpty && !speechService.isRecording {
                    VStack(spacing: 16) {
                        Image(systemName: "mic.circle.fill")
                            .font(.system(size: 80))
                            .foregroundStyle(.linearGradient(
                                colors: [.blue, .purple],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))

                        Text("Tippe auf das Mikrofon um zu sprechen")
                            .font(.headline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)

                        Text("Deine Sprache wird in Text umgewandelt")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                }

                // Transcribed Text
                if !speechService.transcribedText.isEmpty {
                    ScrollView {
                        Text(speechService.transcribedText)
                            .font(.body)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .frame(maxHeight: 300)
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(16)
                    .padding(.horizontal)
                }

                // Error Message
                if let error = speechService.errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(8)
                        .padding(.horizontal)
                }

                Spacer()

                // Audio Level Indicator
                if speechService.isRecording {
                    AudioLevelView(level: speechService.audioLevel)
                        .frame(height: 60)
                        .padding(.horizontal)
                }

                // Record Button
                VStack(spacing: 16) {
                    Button {
                        Task {
                            await speechService.toggleRecording()
                        }
                    } label: {
                        ZStack {
                            Circle()
                                .fill(speechService.isRecording ? Color.red : Color.blue)
                                .frame(width: 80, height: 80)
                                .shadow(color: (speechService.isRecording ? Color.red : Color.blue).opacity(0.4), radius: 10, x: 0, y: 5)

                            if speechService.isRecording {
                                // Pulsing animation
                                Circle()
                                    .stroke(Color.red.opacity(0.5), lineWidth: 3)
                                    .frame(width: 100, height: 100)
                                    .scaleEffect(speechService.isRecording ? 1.2 : 1.0)
                                    .opacity(speechService.isRecording ? 0 : 1)
                                    .animation(.easeInOut(duration: 1).repeatForever(autoreverses: false), value: speechService.isRecording)
                            }

                            Image(systemName: speechService.isRecording ? "stop.fill" : "mic.fill")
                                .font(.title)
                                .foregroundColor(.white)
                        }
                    }
                    .disabled(!speechService.isAuthorized)

                    Text(speechService.isRecording ? "Tippe zum Stoppen" : "Tippe zum Aufnehmen")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.bottom, 32)
            }
            .navigationTitle("Spracheingabe")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Abbrechen") {
                        speechService.stopRecording()
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Speichern") {
                        showingSaveOptions = true
                    }
                    .disabled(speechService.transcribedText.isEmpty)
                    .fontWeight(.semibold)
                }
            }
            .confirmationDialog("Speichern als", isPresented: $showingSaveOptions) {
                Button("Als Notiz speichern") {
                    onSave(speechService.transcribedText)
                    dismiss()
                }
                Button("Als Aufgabe speichern") {
                    onSave("TODO:" + speechService.transcribedText)
                    dismiss()
                }
                Button("Abbrechen", role: .cancel) {}
            }
        }
        .interactiveDismissDisabled(speechService.isRecording)
    }
}

// MARK: - Audio Level View
struct AudioLevelView: View {
    let level: Float
    let barCount: Int = 20

    var body: some View {
        HStack(spacing: 3) {
            ForEach(0..<barCount, id: \.self) { index in
                RoundedRectangle(cornerRadius: 2)
                    .fill(barColor(for: index))
                    .frame(width: 8)
                    .frame(height: barHeight(for: index))
                    .animation(.easeOut(duration: 0.1), value: level)
            }
        }
    }

    private func barHeight(for index: Int) -> CGFloat {
        let normalizedIndex = Float(index) / Float(barCount)
        let threshold = normalizedIndex
        if level > threshold {
            return CGFloat(20 + (level - threshold) * 40)
        }
        return 20
    }

    private func barColor(for index: Int) -> Color {
        let normalizedIndex = Float(index) / Float(barCount)
        if normalizedIndex < 0.5 {
            return .green
        } else if normalizedIndex < 0.75 {
            return .yellow
        } else {
            return .red
        }
    }
}

// MARK: - Floating Voice Button
struct FloatingVoiceButton: View {
    let action: () -> Void

    @State private var isAnimating = false

    var body: some View {
        Button(action: action) {
            ZStack {
                Circle()
                    .fill(LinearGradient(
                        colors: [.blue, .purple],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(width: 60, height: 60)
                    .shadow(color: .purple.opacity(0.4), radius: 10, x: 0, y: 5)

                Image(systemName: "mic.fill")
                    .font(.title2)
                    .foregroundColor(.white)
            }
        }
        .scaleEffect(isAnimating ? 1.05 : 1.0)
        .animation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true), value: isAnimating)
        .onAppear {
            isAnimating = true
        }
    }
}

// MARK: - Preview
#Preview {
    VoiceInputView { text in
        print("Saved: \(text)")
    }
}

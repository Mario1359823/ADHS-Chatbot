import Foundation
import Speech
import AVFoundation

// MARK: - Speech Recognition Service
@MainActor
class SpeechRecognitionService: ObservableObject {
    @Published var transcribedText: String = ""
    @Published var isRecording: Bool = false
    @Published var isAuthorized: Bool = false
    @Published var errorMessage: String?
    @Published var audioLevel: Float = 0.0

    private var audioEngine: AVAudioEngine?
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?

    init() {
        // Initialize with German locale
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "de-DE"))
        checkAuthorization()
    }

    // MARK: - Authorization

    func checkAuthorization() {
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            Task { @MainActor in
                switch status {
                case .authorized:
                    self?.isAuthorized = true
                case .denied, .restricted, .notDetermined:
                    self?.isAuthorized = false
                    self?.errorMessage = "Spracherkennung nicht autorisiert. Bitte in den Einstellungen aktivieren."
                @unknown default:
                    self?.isAuthorized = false
                }
            }
        }
    }

    func requestMicrophonePermission() async -> Bool {
        await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
    }

    // MARK: - Recording

    func startRecording() async {
        guard isAuthorized else {
            errorMessage = "Spracherkennung nicht autorisiert"
            return
        }

        let micPermission = await requestMicrophonePermission()
        guard micPermission else {
            errorMessage = "Mikrofon-Zugriff nicht erlaubt"
            return
        }

        // Reset previous recording
        stopRecording()
        transcribedText = ""
        errorMessage = nil

        do {
            try await setupAudioSession()
            try startAudioEngine()
            isRecording = true
        } catch {
            errorMessage = "Fehler beim Starten der Aufnahme: \(error.localizedDescription)"
            isRecording = false
        }
    }

    func stopRecording() {
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()

        recognitionRequest = nil
        recognitionTask = nil
        audioEngine = nil

        isRecording = false
        audioLevel = 0.0
    }

    // MARK: - Audio Setup

    private func setupAudioSession() async throws {
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
    }

    private func startAudioEngine() throws {
        audioEngine = AVAudioEngine()
        guard let audioEngine = audioEngine else {
            throw SpeechError.audioEngineError
        }

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            throw SpeechError.requestError
        }

        recognitionRequest.shouldReportPartialResults = true
        recognitionRequest.requiresOnDeviceRecognition = false

        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, _ in
            self?.recognitionRequest?.append(buffer)
            self?.updateAudioLevel(buffer: buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()

        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            Task { @MainActor in
                if let result = result {
                    self?.transcribedText = result.bestTranscription.formattedString
                }

                if let error = error {
                    self?.errorMessage = "Erkennungsfehler: \(error.localizedDescription)"
                    self?.stopRecording()
                }
            }
        }
    }

    private func updateAudioLevel(buffer: AVAudioPCMBuffer) {
        guard let channelData = buffer.floatChannelData?[0] else { return }
        let frames = buffer.frameLength

        var sum: Float = 0
        for i in 0..<Int(frames) {
            sum += abs(channelData[i])
        }
        let average = sum / Float(frames)

        Task { @MainActor in
            self.audioLevel = min(average * 10, 1.0)
        }
    }

    // MARK: - Toggle Recording

    func toggleRecording() async {
        if isRecording {
            stopRecording()
        } else {
            await startRecording()
        }
    }

    // MARK: - Change Language

    func setLanguage(_ locale: Locale) {
        speechRecognizer = SFSpeechRecognizer(locale: locale)
    }
}

// MARK: - Speech Errors
enum SpeechError: Error, LocalizedError {
    case audioEngineError
    case requestError
    case notAuthorized

    var errorDescription: String? {
        switch self {
        case .audioEngineError:
            return "Audio Engine konnte nicht gestartet werden"
        case .requestError:
            return "Spracherkennungsanfrage konnte nicht erstellt werden"
        case .notAuthorized:
            return "Spracherkennung nicht autorisiert"
        }
    }
}

// MARK: - Supported Languages
extension SpeechRecognitionService {
    static let supportedLanguages: [(name: String, locale: Locale)] = [
        ("Deutsch", Locale(identifier: "de-DE")),
        ("English", Locale(identifier: "en-US")),
        ("Français", Locale(identifier: "fr-FR")),
        ("Español", Locale(identifier: "es-ES")),
        ("Italiano", Locale(identifier: "it-IT"))
    ]
}

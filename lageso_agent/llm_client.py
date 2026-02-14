"""
Ollama-Client für den LaGeSo-Befundbericht-Generator.
Kommuniziert mit dem lokalen Ollama-Server über HTTP.
"""

import json
import re
import requests
from typing import Optional

from prompts import SYSTEM_PROMPT

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
REQUEST_TIMEOUT = 120  # Sekunden


class OllamaClient:
    """Client für die Kommunikation mit Ollama."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def test_connection(self) -> tuple[bool, str]:
        """Testet die Verbindung zum Ollama-Server.

        Returns:
            Tuple (Erfolg, Nachricht)
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if self.model in models:
                    return True, f"Verbunden. Modell '{self.model}' verfügbar."
                # Check for model name without tag
                base_names = [m.split(":")[0] for m in models]
                model_base = self.model.split(":")[0]
                if model_base in base_names:
                    return True, f"Verbunden. Modell '{self.model}' verfügbar."
                available = ", ".join(models) if models else "keine"
                return False, (
                    f"Verbunden, aber Modell '{self.model}' nicht gefunden. "
                    f"Verfügbare Modelle: {available}"
                )
            return False, f"Ollama antwortet mit Status {resp.status_code}"
        except requests.ConnectionError:
            return False, (
                "Ollama ist nicht erreichbar. "
                "Bitte starten Sie Ollama mit 'ollama serve'."
            )
        except requests.Timeout:
            return False, "Zeitüberschreitung bei Verbindung zu Ollama."
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}"

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Sendet einen Prompt an Ollama und gibt die Antwort zurück.

        Args:
            prompt: Der User-Prompt
            system: Optionaler System-Prompt (Default: SYSTEM_PROMPT)

        Returns:
            Die generierte Antwort als String

        Raises:
            ConnectionError: Wenn Ollama nicht erreichbar ist
            TimeoutError: Bei Zeitüberschreitung
            RuntimeError: Bei sonstigen Fehlern
        """
        if system is None:
            system = SYSTEM_PROMPT

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 4096,
            },
        }

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except requests.ConnectionError:
            raise ConnectionError(
                "Ollama ist nicht erreichbar. "
                "Bitte starten Sie Ollama mit 'ollama serve'."
            )
        except requests.Timeout:
            raise TimeoutError(
                f"Zeitüberschreitung ({REQUEST_TIMEOUT}s) bei LLM-Aufruf. "
                "Versuchen Sie es erneut oder verwenden Sie ein kleineres Modell."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Ollama HTTP-Fehler: {e}")

    def extract_json(self, prompt: str, max_retries: int = 3) -> dict:
        """Sendet einen Prompt und extrahiert JSON aus der Antwort.

        Versucht bis zu max_retries Mal, valides JSON zu erhalten.

        Args:
            prompt: Der Prompt, der JSON-Ausgabe erwartet
            max_retries: Maximale Anzahl an Versuchen

        Returns:
            Geparstes JSON als dict

        Raises:
            ValueError: Wenn nach allen Versuchen kein valides JSON
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                raw = self.generate(prompt)
                return self._parse_json(raw)
            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Retry mit klarerer Anweisung
                    prompt = (
                        f"Deine vorherige Antwort war kein valides JSON. "
                        f"Fehler: {str(e)}\n\n"
                        f"Bitte antworte NUR mit einem validen JSON-Objekt, "
                        f"KEIN anderer Text davor oder danach.\n\n"
                        f"Ursprüngliche Aufgabe:\n{prompt}"
                    )

        raise ValueError(
            f"Konnte nach {max_retries} Versuchen kein valides JSON extrahieren. "
            f"Letzter Fehler: {last_error}"
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Versucht JSON aus einem Text zu extrahieren.

        Unterstützt:
        - Reines JSON
        - JSON in ```json ... ``` Code-Blöcken
        - JSON eingebettet in Text (findet erstes { ... } Paar)
        """
        text = text.strip()

        # Versuch 1: Direktes Parsen
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Versuch 2: JSON aus Code-Block extrahieren
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Versuch 3: Erstes JSON-Objekt finden (Klammer-Matching)
        brace_start = text.find("{")
        if brace_start != -1:
            depth = 0
            for i in range(brace_start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[brace_start : i + 1])
                        except json.JSONDecodeError:
                            break

        raise ValueError(f"Kein valides JSON in der Antwort gefunden.")

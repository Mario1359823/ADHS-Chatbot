#!/usr/bin/env bash
#
# Startskript für den LaGeSo Befundbericht Generator.
# Prüft Voraussetzungen und startet Streamlit.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  LaGeSo Befundbericht Generator"
echo "============================================"
echo ""

# --- Python prüfen ---
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python 3 ist nicht installiert."
    echo "Bitte installieren Sie Python 3.9 oder höher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python: $PYTHON_VERSION"

# --- pip-Abhängigkeiten prüfen ---
echo "Prüfe Abhängigkeiten..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installiere Abhängigkeiten..."
    pip3 install -r requirements.txt
fi

# --- Ollama prüfen ---
echo ""
if command -v ollama &> /dev/null; then
    echo "Ollama: installiert"
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama-Server: läuft"
        MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = [m['name'] for m in data.get('models', [])]
print(', '.join(models) if models else 'keine Modelle geladen')
" 2>/dev/null || echo "Fehler beim Abrufen")
        echo "Verfügbare Modelle: $MODELS"
    else
        echo "WARNUNG: Ollama ist installiert, aber der Server läuft nicht."
        echo "Starten Sie Ollama mit: ollama serve"
        echo ""
        echo "Die App wird trotzdem gestartet. Sie können Ollama später starten"
        echo "und die Verbindung in der App testen."
    fi
else
    echo "WARNUNG: Ollama ist nicht installiert."
    echo "Installieren Sie Ollama von: https://ollama.ai"
    echo ""
    echo "Die App wird trotzdem gestartet."
fi

# --- Streamlit starten ---
echo ""
echo "Starte Streamlit..."
echo "Die App öffnet sich im Browser unter: http://localhost:8501"
echo ""

python3 -m streamlit run app.py \
    --server.headless true \
    --server.port 8501 \
    --browser.gatherUsageStats false

#!/bin/bash
# Doppelklick im Finder startet den Live-Editor (öffnet Terminal + Browser). Beenden: Strg+C oder Fenster schließen.
cd "$(dirname "$0")" || exit 1
python3 editor.py

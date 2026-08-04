#!/bin/bash
# Startet die Fotobox im Vollbild-Kiosk-Modus.
# Als ExecStart der fotobox.service systemd-Unit eingebunden.
set -euo pipefail

FOTOBOX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$FOTOBOX_DIR"

# Bildschirmschoner und Energiesparmodus deaktivieren, Mauszeiger ausblenden.
xset s off || true
xset -dpms || true
xset s noblank || true
unclutter -idle 0.5 -root &

exec python3 -m fotobox.main --config "${FOTOBOX_CONFIG:-$HOME/.fotobox/config.yaml}"

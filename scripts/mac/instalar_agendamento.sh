#!/usr/bin/env bash
# Cria o agendamento diário às 00:00 no Mac (launchd). Não precisa de sudo.
#   ./scripts/mac/instalar_agendamento.sh            instala
#   ./scripts/mac/instalar_agendamento.sh remover    remove
#
# Para o Mac acordar sozinho às 23:55 (precisa de senha de administrador, rode você mesmo):
#   sudo pmset repeat wakeorpoweron MTWRFSU 23:55:00
set -euo pipefail
ROTULO="br.calendarios-forenses.robo"
PLIST="$HOME/Library/LaunchAgents/$ROTULO.plist"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "remover" ]]; then
  launchctl bootout "gui/$(id -u)/$ROTULO" 2>/dev/null || true
  rm -f "$PLIST"; echo "removido"; exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents"
cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$ROTULO</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$RAIZ/scripts/mac/rodar_noite.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>0</integer><key>Minute</key><integer>0</integer></dict>
  <key>RunAtLoad</key><false/>
</dict></plist>
PLIST
launchctl bootout "gui/$(id -u)/$ROTULO" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "agendado: todo dia às 00:00. Log em ~/Library/Logs/calendarios-forenses.log"

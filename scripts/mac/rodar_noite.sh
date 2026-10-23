#!/usr/bin/env bash
# Robô da meia-noite, versão Mac. Roda os motores, grava dados/ e envia ao GitHub.
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG="$HOME/Library/Logs/calendarios-forenses.log"
exec >>"$LOG" 2>&1
echo "=== $(date '+%F %T') ==="
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

git pull --rebase --autostash || { echo "pull falhou"; exit 1; }
python3 -W error -m unittest discover -s tests || { echo "testes falharam: não rodo com código quebrado"; exit 1; }
python3 -m robo.executar   # falha de um motor não impede gravar os outros

git add dados
if git diff --cached --quiet; then
  echo "sem mudanças"
else
  git commit -q -m "dados: atualização automática $(date +%F)"
  git push || echo "push falhou"
fi

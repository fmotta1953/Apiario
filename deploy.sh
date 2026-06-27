#!/bin/bash
# Aggiorna la versione cache nel service worker e fa il push su GitHub
set -e
cd "$(dirname "$0")"

# Incrementa il numero di versione in sw.js
CURRENT=$(grep -o "apiario-v[0-9]*" sw.js | grep -o "[0-9]*")
NEXT=$((CURRENT + 1))
sed -i '' "s/apiario-v${CURRENT}/apiario-v${NEXT}/" sw.js
echo "Cache: v${CURRENT} → v${NEXT}"

git add -A
git commit -m "Deploy v${NEXT}"
git push
echo "✅ Deploy completato — chiudi e riapri l'app sul telefono"

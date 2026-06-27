#!/bin/bash
set -e
cd "$(dirname "$0")"

# Incrementa cache SW
SWVER=$(grep -o "apiario-v[0-9]*" sw.js | grep -o "[0-9]*")
SWNEXT=$((SWVER + 1))
sed -i '' "s/apiario-v${SWVER}/apiario-v${SWNEXT}/" sw.js

# Incrementa version.json
APPVER=$(python3 -c "import json;d=json.load(open('version.json'));print(d['v'])")
APPNEXT=$((APPVER + 1))
echo "{\"v\":${APPNEXT}}" > version.json

# Aggiorna numero versione visibile nell'app
sed -i '' "s/>v[0-9]*<\/span>/>v${APPNEXT}<\/span>/" index.html

echo "SW: v${SWVER}→v${SWNEXT} | App: v${APPVER}→v${APPNEXT}"

git add -A
git commit -m "Deploy app-v${APPNEXT}"
git push
echo "✅ Fatto — riapri l'app sul telefono"

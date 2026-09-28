#!/usr/bin/env python3
"""Trasforma index.html (PWA) in apiario.html (bundle Swift).

Rimuove le parti che non hanno senso su file:// dentro WKWebView:
- <link rel="manifest"> e <link rel="apple-touch-icon"> (riferimenti rotti)
- l'ultimo blocco <script> con registrazione service worker e check version.json

Inietta il bridge nativo (no-op nella PWA in browser, guard esplicita):
- syncPush() inoltra il DB al nativo via webkit.messageHandlers.sync (iCloud);
  all'avvio unisce i dati locali con quelli di iCloud (window.__REMOTE_DB__)
- exportFile() e stampa() passano al nativo (share sheet / stampa iOS)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).parent / "index.html"
DST = Path(__file__).parent.parent / "Apiario" / "apiario.html"


def transform(html: str) -> str:
    # Rimuovi link manifest / apple-touch-icon
    html = re.sub(r'^\s*<link rel="(manifest|apple-touch-icon)"[^>]*>\s*\n', "", html, flags=re.M)

    # Rimuovi il blocco SW/version-check (l'ultimo <script> prima di </body>)
    pattern = re.compile(
        r"<script>\s*\nif\('serviceWorker' in navigator\).*?</script>\s*\n(?=</body>)",
        re.S,
    )
    html, n = pattern.subn("", html)
    if n != 1:
        sys.exit(f"ERRORE: blocco service-worker trovato {n} volte (atteso 1). Sync annullato.")

    # Inietta il bridge iCloud prima di </body>
    for fn in ("save", "syncPush", "syncMerge", "exportFile", "stampa"):
        if f"function {fn}(" not in html:
            sys.exit(f"ERRORE: {fn}() non trovata in index.html. Sync annullato.")
    html, n = re.subn(r"(?=</body>)", BRIDGE + "\n", html, count=1)
    if n != 1:
        sys.exit("ERRORE: </body> non trovato. Sync annullato.")
    return html


BRIDGE = """\
<script>
/* Bridge nativo — iniettato da sync-swift.py, assente nella PWA */
(function(){
  if(!(window.webkit&&webkit.messageHandlers&&webkit.messageHandlers.sync))return
  var h=webkit.messageHandlers
  window.__NATIVE__=true
  // save() chiama syncPush(): il nativo comprime e salva in iCloud
  syncPush=function(){try{h.sync.postMessage(JSON.stringify(db))}catch(e){}}
  // WKWebView ignora download di blob e window.print(): li gestisce il nativo
  if(h.exportFile)exportFile=function(name,text){h.exportFile.postMessage({name:name,text:text})}
  if(h.print)stampa=function(){h.print.postMessage('')}
  if(h.lang)h.lang.postMessage(LANG)
  // Avvio: unisci con la copia in iCloud iniettata dal nativo (o inviala se iCloud è vuoto)
  if(window.__REMOTE_DB__)syncMerge(window.__REMOTE_DB__);else syncPush()
})()
</script>"""


def main() -> None:
    if not SRC.exists():
        sys.exit(f"ERRORE: {SRC} non trovato")
    DST.write_text(transform(SRC.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"✅ Sync: {SRC.name} → {DST.relative_to(DST.parent.parent)}")


if __name__ == "__main__":
    main()

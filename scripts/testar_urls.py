"""Testa, a partir de ONDE ESTE SCRIPT RODA, se as URLs respondem ao robô.

Serve para saber se uma fonte funciona na nuvem: rode pelo workflow `testar-urls`
(GitHub), nunca confie só no teste feito no seu computador.
Uso: python3 scripts/testar_urls.py URL [URL ...]
"""
from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, ".")
from robo.rede import USER_AGENT, Cliente  # noqa: E402


def main(urls) -> None:
    c = Cliente()
    for url in urls:
        inicio = time.monotonic()
        if not c._permitido(url):
            print("ROBOTS-NEGA", url)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                corpo = r.read()
                print("OK", r.status, len(corpo), r.headers.get("Content-Type", ""), round(time.monotonic() - inicio, 1), url)
        except urllib.error.HTTPError as e:
            print("ERRO", e.code, url)
        except Exception as e:
            print("ERRO", type(e).__name__, str(e)[:60], url)
        time.sleep(2)


if __name__ == "__main__":
    main(sys.argv[1:])

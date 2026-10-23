"""Sonda: de onde o robô roda, quais sites de tribunal respondem?

Faz UMA requisição GET na página inicial de cada tribunal (com o User-Agent do robô, sem
disfarce) e imprime status e tempo. Serve para decidir onde cada motor pode rodar.
Uso: python3 scripts/sondar_dominios.py > sonda.json
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, ".")
from robo.registro import todos_os_tribunais  # noqa: E402
from robo.rede import USER_AGENT  # noqa: E402

UFS = {"AC": "ac", "AL": "al", "AP": "ap", "AM": "am", "BA": "ba", "CE": "ce", "DF": "dft", "ES": "es",
       "GO": "go", "MA": "ma", "MT": "mt", "MS": "ms", "MG": "mg", "PA": "pa", "PB": "pb", "PR": "pr",
       "PE": "pe", "PI": "pi", "RJ": "rj", "RN": "rn", "RS": "rs", "RO": "ro", "RR": "rr", "SC": "sc",
       "SP": "sp", "SE": "se", "TO": "to"}


def dominio(sigla: str) -> str:
    if sigla in ("STF", "STJ", "TST", "TSE", "STM"):
        return sigla.lower() + ".jus.br"
    if sigla.startswith("TJM"):
        return "tjm" + sigla[3:].lower() + ".jus.br"
    if sigla == "TJDFT":
        return "tjdft.jus.br"
    if sigla.startswith("TJ"):
        return "tj" + sigla[2:].lower() + ".jus.br"
    if sigla.startswith("TRF") or sigla.startswith("TRT"):
        return sigla.lower() + ".jus.br"
    if sigla.startswith("TRE"):
        return "tre-" + sigla[3:].lower() + ".jus.br"
    return ""


def sondar(host: str) -> dict:
    inicio = time.monotonic()
    req = urllib.request.Request("https://www." + host + "/", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return {"host": host, "status": r.status, "seg": round(time.monotonic() - inicio, 1)}
    except urllib.error.HTTPError as e:
        return {"host": host, "status": e.code, "seg": round(time.monotonic() - inicio, 1)}
    except Exception as e:
        return {"host": host, "status": None, "erro": type(e).__name__ + ": " + str(e)[:80],
                "seg": round(time.monotonic() - inicio, 1)}


def main() -> None:
    saida = []
    for t in todos_os_tribunais():
        d = dominio(t["sigla"])
        r = sondar(d)
        r["sigla"] = t["sigla"]
        saida.append(r)
        time.sleep(1.5)
    json.dump(saida, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()

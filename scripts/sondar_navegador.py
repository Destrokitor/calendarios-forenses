"""Sonda com navegador real (Chromium headless) para os sites que recusam o robô simples.

Sem disfarce: não muda User-Agent, não usa plugin "stealth", não resolve CAPTCHA, não
mexe em fingerprint. Se o site mostrar uma tela de verificação, a sonda registra
"desafio" e PARA de insistir naquele site.
Uso: python3 scripts/sondar_navegador.py sonda_navegador.json sonda_gh2/sonda.json
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, ".")
from playwright.sync_api import sync_playwright  # noqa: E402

MARCAS_DE_DESAFIO = ("just a moment", "attention required", "access denied", "captcha",
                     "verifying you are human", "checking your browser", "request blocked")


def main(saida: str, anterior: str) -> None:
    antes = json.load(open(anterior, encoding="utf-8"))
    alvos = [r for r in antes if not (r["status"] is not None and r["status"] < 400)]
    resultado = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for r in alvos:
            pagina = nav.new_page()
            item = {"sigla": r["sigla"], "host": r["host"]}
            try:
                resp = pagina.goto("https://www." + r["host"] + "/", timeout=30000, wait_until="domcontentloaded")
                titulo = (pagina.title() or "")[:80]
                corpo = (pagina.inner_text("body", timeout=5000) or "")[:400].lower()
                desafio = any(m in titulo.lower() or m in corpo for m in MARCAS_DE_DESAFIO)
                item.update({"status": resp.status if resp else None, "titulo": titulo, "desafio": desafio})
            except Exception as e:
                item.update({"status": None, "erro": type(e).__name__ + ": " + str(e)[:80]})
            pagina.close()
            resultado.append(item)
            time.sleep(2)
        nav.close()
    json.dump(resultado, open(saida, "w", encoding="utf-8"), ensure_ascii=False)
    ok = [r for r in resultado if r.get("status") and r["status"] < 400 and not r.get("desafio")]
    print("abriram sem desafio:", len(ok), "de", len(resultado))
    for r in resultado:
        print(r["sigla"], r.get("status"), "DESAFIO" if r.get("desafio") else "", r.get("titulo", r.get("erro", "")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

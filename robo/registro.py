"""Lista de todos os tribunais cobertos pelo projeto (92) e quem ainda não tem motor.

Fonte da contagem: ver docs/LEVANTAMENTO_TRIBUNAIS.md. A lista é construída aqui, e não
à mão em outro lugar, para que `dados/cobertura.json` sempre mostre os 92, inclusive os
que ainda estão sem motor ("indisponivel").
"""
from __future__ import annotations

from typing import Dict, List

_UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def todos_os_tribunais() -> List[Dict[str, str]]:
    """Cada item: sigla, nome, justica. A sigla é a chave em `dados/` e na cobertura."""
    lista: List[Dict[str, str]] = []

    for sigla, nome in [
        ("STF", "Supremo Tribunal Federal"),
        ("STJ", "Superior Tribunal de Justiça"),
        ("TST", "Tribunal Superior do Trabalho"),
        ("TSE", "Tribunal Superior Eleitoral"),
        ("STM", "Superior Tribunal Militar"),
    ]:
        lista.append({"sigla": sigla, "nome": nome, "justica": "superior"})

    for uf in _UFS:
        sigla = "TJDFT" if uf == "DF" else "TJ" + uf
        nome = "Tribunal de Justiça do Distrito Federal e dos Territórios" if uf == "DF" else "Tribunal de Justiça (" + uf + ")"
        lista.append({"sigla": sigla, "nome": nome, "justica": "estadual"})

    for uf in ("SP", "MG", "RS"):
        lista.append({"sigla": "TJM" + uf, "nome": "Tribunal de Justiça Militar (" + uf + ")", "justica": "militar_estadual"})

    for n in range(1, 7):
        lista.append({"sigla": "TRF%d" % n, "nome": "Tribunal Regional Federal da %dª Região" % n, "justica": "federal"})

    for n in range(1, 25):
        lista.append({"sigla": "TRT%d" % n, "nome": "Tribunal Regional do Trabalho da %dª Região" % n, "justica": "trabalho"})

    for uf in _UFS:
        lista.append({"sigla": "TRE" + uf, "nome": "Tribunal Regional Eleitoral (" + uf + ")", "justica": "eleitoral"})

    return lista

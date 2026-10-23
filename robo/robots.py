"""robots.txt conforme a RFC 9309 (o padrão da web), porque o `urllib.robotparser` do Python
foge dele em dois pontos que bloquearam fontes legítimas:

  1. Para ele, 401/403 ao buscar robots.txt significa "proibido tudo". Pela RFC, qualquer
     4xx significa "arquivo não disponível": o robô PODE acessar. Só 5xx ou rede fora do ar
     significa "assuma que tudo é proibido" (tratado em rede.py).
  2. Para ele vale a PRIMEIRA regra que casa; pela RFC vale a MAIS ESPECÍFICA (a de padrão mais
     longo), e em empate vence o Allow. Ex.: `Disallow: /` + `Allow: /portal` libera /portal.

O que continua valendo, sem exceção: se o site proíbe o caminho para o nosso robô, não
acessamos.
"""
from __future__ import annotations

import re
from typing import List, Tuple

Regra = Tuple[bool, str]  # (permite?, padrão)


def _agrupar(texto: str) -> List[Tuple[List[str], List[Regra]]]:
    grupos: List[Tuple[List[str], List[Regra]]] = []
    agentes: List[str] = []
    regras: List[Regra] = []
    lendo_regras = False
    for linha in texto.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if ":" not in linha:
            continue
        campo, valor = (p.strip() for p in linha.split(":", 1))
        campo = campo.lower()
        if campo == "user-agent":
            if lendo_regras:
                grupos.append((agentes, regras))
                agentes, regras, lendo_regras = [], [], False
            agentes.append(valor.lower())
        elif campo in ("allow", "disallow"):
            lendo_regras = True
            if valor:  # "Disallow:" vazio = libera tudo; não gera regra
                regras.append((campo == "allow", valor))
    if agentes:
        grupos.append((agentes, regras))
    return grupos


def _casa(padrao: str, caminho: str) -> bool:
    fim = padrao.endswith("$")
    if fim:
        padrao = padrao[:-1]
    expr = "".join(".*" if c == "*" else re.escape(c) for c in padrao)
    return re.match(expr + ("$" if fim else ""), caminho) is not None


def permitido(texto_robots: str, agente: str, caminho: str) -> bool:
    """`agente` é o nome do robô (ex.: "calendarios-forenses-robo"); `caminho` inclui a query."""
    agente = agente.lower()
    grupos = _agrupar(texto_robots)
    especificos = [r for ags, r in grupos if any(a != "*" and a in agente for a in ags)]
    escolhidos = especificos or [r for ags, r in grupos if "*" in ags]
    regras = [x for g in escolhidos for x in g]
    melhor_tamanho, melhor_permite = -1, True
    for permite, padrao in regras:
        if _casa(padrao, caminho):
            tamanho = len(padrao)
            if tamanho > melhor_tamanho or (tamanho == melhor_tamanho and permite):
                melhor_tamanho, melhor_permite = tamanho, permite
    return melhor_permite

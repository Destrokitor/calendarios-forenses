"""Verificações que todo calendário precisa passar antes de ser gravado.

Se qualquer uma falhar, o robô NÃO grava: mantém o dado anterior e marca o tribunal
como desatualizado. É melhor o app dizer "não consegui verificar" do que usar um
calendário lido pela metade.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict, List

from .modelo import TIPOS, todos_os_dias


def validar(cal: Dict[str, Any], sigla: str, ano: int, esperado: Dict[str, Any]) -> List[str]:
    """Devolve a lista de problemas (vazia = válido).

    `esperado` vem do motor:
      min_geral         - mínimo de dias gerais (um calendário com 3 dias foi lido pela metade)
      min_locais        - mínimo de locais conhecidos
      ancoras           - datas conferidas À MÃO que têm de estar em `geral` (detecta
                          quebra silenciosa de leitura), ex.: {"2026-10-28": "Dia do Servidor"}
      exige_recesso     - se True, tem de haver ao menos um dia do tipo "recesso"
    """
    erros: List[str] = []

    if cal.get("tribunal") != sigla:
        erros.append("tribunal no arquivo (%r) diferente do esperado (%r)" % (cal.get("tribunal"), sigla))
    if cal.get("ano") != ano:
        erros.append("ano no arquivo (%r) diferente do esperado (%r)" % (cal.get("ano"), ano))
    if not cal.get("fontes"):
        erros.append("sem nenhuma fonte registrada")

    vistos = set()
    for dia in todos_os_dias(cal):
        try:
            data = datetime.date.fromisoformat(dia["data"])
        except (KeyError, ValueError, TypeError):
            erros.append("data inválida: %r" % (dia,))
            continue
        if data.year != ano:
            erros.append("data fora do ano %d: %s" % (ano, dia["data"]))
        if dia.get("tipo") not in TIPOS:
            erros.append("tipo desconhecido: %r" % (dia.get("tipo"),))
        if not dia.get("motivo"):
            erros.append("dia sem motivo: %s" % dia["data"])
        if not dia.get("fonte"):
            erros.append("dia sem fonte: %s" % dia["data"])
        if dia.get("tipo") == "parcial" and not dia.get("horario"):
            erros.append("dia parcial sem horário: %s" % dia["data"])
    fontes_ids = {f.get("id") for f in cal.get("fontes", [])}
    for dia in todos_os_dias(cal):
        if dia.get("fonte") and dia["fonte"] not in fontes_ids:
            erros.append("dia aponta para fonte inexistente %r" % dia["fonte"])
            break

    for nome, lista in cal.get("locais", {}).items():
        chaves = [(d["data"], d["tipo"], d["motivo"]) for d in lista if "data" in d]
        if len(chaves) != len(set(chaves)):
            erros.append("dias repetidos em %s" % nome)
        if nome != " ".join(nome.strip().upper().split()):
            erros.append("nome de local fora do padrão: %r" % nome)
    chaves_g = [(d["data"], d["tipo"], d["motivo"]) for d in cal.get("geral", []) if "data" in d]
    if len(chaves_g) != len(set(chaves_g)):
        erros.append("dias gerais repetidos")

    if len(cal.get("geral", [])) < esperado.get("min_geral", 1):
        erros.append("poucos dias gerais (%d < %d)" % (len(cal.get("geral", [])), esperado.get("min_geral", 1)))
    if len(cal.get("locais", {})) < esperado.get("min_locais", 0):
        erros.append("poucos locais (%d < %d)" % (len(cal.get("locais", {})), esperado.get("min_locais", 0)))

    datas_gerais = {d["data"] for d in cal.get("geral", []) if "data" in d}
    for data, nome in esperado.get("ancoras", {}).items():
        if data not in datas_gerais:
            erros.append("data âncora ausente: %s (%s)" % (data, nome))

    if esperado.get("exige_recesso") and not any(d.get("tipo") == "recesso" for d in cal.get("geral", [])):
        erros.append("esperava dias de recesso e não achou nenhum")

    return erros

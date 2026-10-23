"""O contrato dos dados: o que um motor devolve e o que o robô aceita gravar.

Formato de `dados/<SIGLA>/<ANO>.json`:

    {
      "tribunal": "TJSP",
      "ano": 2026,
      "gerado_em": "2026-10-24T03:00:00Z",
      "fontes": [{"id": "provimento", "url": "https://...", "descricao": "..."}],
      "geral":  [Dia, ...],            # vale para o tribunal inteiro
      "locais": {"ADAMANTINA": [Dia, ...], "AGUAÍ": []}   # comarca/foro/município
    }

    Dia = {"data": "2026-02-16", "tipo": "sem_expediente", "motivo": "Carnaval",
           "fonte": "provimento"}            # "horario" só no tipo "parcial"

`locais` tem uma chave para TODO local conhecido, mesmo sem dia próprio (lista vazia):
é daí que o app monta a lista de escolha de comarca.

Tipos de dia:
  sem_expediente  - o fórum não abre; prazo não corre (ou vencimento é prorrogado)
  recesso         - dia dentro de recesso forense
  suspensao_prazo - prazos suspensos por ato do tribunal (expediente pode existir)
  parcial         - expediente encerrado antes ou iniciado depois da hora normal
                    (CPC art. 224 §1º): o dia conta, mas não pode ser começo nem fim
"""
from __future__ import annotations

import copy
import datetime
from typing import Any, Dict, List

TIPOS = ("sem_expediente", "recesso", "suspensao_prazo", "parcial")


def dia(data: datetime.date, tipo: str, motivo: str, fonte: str, horario: str = "") -> Dict[str, str]:
    """Monta um Dia. Usar sempre esta função para não errar o nome dos campos."""
    item = {"data": data.isoformat(), "tipo": tipo, "motivo": motivo, "fonte": fonte}
    if horario:
        item["horario"] = horario
    return item


def calendario_vazio(sigla: str, ano: int) -> Dict[str, Any]:
    return {"tribunal": sigla, "ano": ano, "gerado_em": "", "fontes": [], "geral": [], "locais": {}}


def sem_carimbo(cal: Dict[str, Any]) -> Dict[str, Any]:
    """Cópia sem `gerado_em`: serve para saber se o CONTEÚDO mudou, para o robô não
    criar commit todo dia só porque a hora mudou."""
    c = copy.deepcopy(cal)
    c["gerado_em"] = ""
    return c


def normalizar_local(nome: str) -> str:
    """Chave de comarca: maiúscula, espaços únicos. Mantém acento (AGUAÍ, não AGUAI)."""
    return " ".join(nome.strip().upper().split())


def ordenar(cal: Dict[str, Any]) -> Dict[str, Any]:
    """Deixa a saída determinística: dias por data, locais por nome."""
    chave = lambda d: (d["data"], d["tipo"], d["motivo"])  # noqa: E731
    cal["geral"] = sorted(cal["geral"], key=chave)
    cal["locais"] = {k: sorted(v, key=chave) for k, v in sorted(cal["locais"].items())}
    return cal


def todos_os_dias(cal: Dict[str, Any]) -> List[Dict[str, str]]:
    dias = list(cal["geral"])
    for lista in cal["locais"].values():
        dias.extend(lista)
    return dias

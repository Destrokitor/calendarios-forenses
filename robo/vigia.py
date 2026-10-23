"""Vigia: confere se os dados estão frescos. Roda no GitHub, independente do Mac.

Falha (saída 1, e o GitHub manda e-mail) se:
  - `dados/cobertura.json` não existe ou foi gerado há mais de MAX_DIAS dias
    (o robô da meia-noite parou de rodar);
  - algum tribunal com motor está sem leitura boa do ano corrente há mais de MAX_DIAS dias.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from typing import List

from .executar import RAIZ

MAX_DIAS = 2


def _data(texto: str) -> datetime.datetime:
    return datetime.datetime.strptime(texto, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def verificar(raiz: str, agora: datetime.datetime) -> List[str]:
    caminho = os.path.join(raiz, "dados", "cobertura.json")
    if not os.path.exists(caminho):
        return ["dados/cobertura.json não existe: o robô nunca rodou"]
    with open(caminho, encoding="utf-8") as f:
        cob = json.load(f)
    limite = datetime.timedelta(days=MAX_DIAS)
    problemas: List[str] = []
    if agora - _data(cob["gerado_em"]) > limite:
        problemas.append("cobertura gerada em %s: o robô parou de rodar" % cob["gerado_em"])
    for sigla, t in cob["tribunais"].items():
        if t["status"] == "sem_motor":
            continue
        corrente = t["anos"].get(str(agora.year), {})
        ok = corrente.get("ultima_ok")
        if not ok:
            problemas.append("%s: nunca teve leitura boa em %d" % (sigla, agora.year))
        elif agora - _data(ok) > limite:
            problemas.append("%s: última leitura boa em %s (erro: %s)" % (sigla, ok, corrente.get("erro")))
    return problemas


def main() -> int:
    problemas = verificar(RAIZ, datetime.datetime.now(datetime.timezone.utc))
    for p in problemas:
        print("ATENÇÃO:", p, file=sys.stderr)
    if not problemas:
        print("tudo fresco")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())

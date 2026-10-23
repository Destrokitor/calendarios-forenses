"""O robô: roda os motores, valida, grava `dados/` e atualiza `dados/cobertura.json`.

Uso:
    python3 -m robo.executar                  # todos os motores
    python3 -m robo.executar --so TJSP        # um só
    python3 -m robo.executar --grupo geral    # só os que rodam nos servidores do GitHub
    python3 -m robo.executar --grupo brasil   # só os que exigem IP brasileiro (runner no Brasil)

Regra de ouro: calendário que falha na validação NÃO é gravado. O arquivo anterior fica,
e a cobertura passa a "desatualizado" com a data da última leitura boa.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

from .modelo import ordenar, sem_carimbo
from .motores import descobrir
from .motores.base import AindaNaoPublicado, Motor
from .rede import Cliente
from .registro import AVISO_INCOMPATIVEL, INCOMPATIVEIS, todos_os_tribunais
from .validacao import validar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _agora() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ler_json(caminho: str, padrao: Any) -> Any:
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return padrao


def _gravar_json(caminho: str, dados: Any) -> None:
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, caminho)  # atômico: ninguém lê arquivo pela metade


def _status(motor: Optional[Motor], ano_corrente: Dict[str, Any], sigla: str = "") -> str:
    if motor is None:
        return "incompativel" if sigla in INCOMPATIVEIS else "sem_motor"
    if ano_corrente.get("erro"):
        return "desatualizado" if ano_corrente.get("ultima_ok") else "indisponivel"
    if ano_corrente.get("ultima_ok"):
        return "parcial" if motor.parcial else "verificado"
    return "indisponivel"


def executar(raiz: str, motores: Dict[str, Motor], hoje: datetime.date, rede: Cliente,
             so: Optional[str] = None, grupo: Optional[str] = None) -> Dict[str, Any]:
    caminho_cob = os.path.join(raiz, "dados", "cobertura.json")
    anterior = _ler_json(caminho_cob, {"tribunais": {}})
    cobertura: Dict[str, Any] = {"gerado_em": _agora(), "tribunais": {}}
    falhas: List[str] = []

    for t in todos_os_tribunais():
        sigla = t["sigla"]
        motor = motores.get(sigla)
        antigo = anterior.get("tribunais", {}).get(sigla, {})
        anos_antigos = antigo.get("anos", {})
        entrada: Dict[str, Any] = {"nome": t["nome"], "justica": t["justica"], "anos": dict(anos_antigos)}

        selecionado = motor is not None and (so is None or so == sigla) and (grupo is None or motor.precisa_ip_brasil == (grupo == "brasil"))
        if selecionado:
            for ano in motor.anos(hoje):
                reg = dict(anos_antigos.get(str(ano), {}))
                reg["ultima_tentativa"] = _agora()
                try:
                    cal = motor.coletar(ano, rede)
                    cal["gerado_em"] = _agora()
                    ordenar(cal)
                    problemas = validar(cal, sigla, ano, motor.esperado)
                    if problemas:
                        raise ValueError("; ".join(problemas[:5]) + (" (+%d)" % (len(problemas) - 5) if len(problemas) > 5 else ""))
                    arquivo = os.path.join(raiz, "dados", sigla, "%d.json" % ano)
                    atual = _ler_json(arquivo, None)
                    if atual is None or sem_carimbo(atual) != sem_carimbo(cal):
                        _gravar_json(arquivo, cal)
                    reg.update({"ultima_ok": cal["gerado_em"], "erro": None, "nao_publicado": False,
                                "dias_gerais": len(cal["geral"]), "locais": len(cal["locais"])})
                except AindaNaoPublicado:
                    reg.update({"nao_publicado": True, "erro": None})
                except Exception as e:  # um motor quebrado não pode derrubar os outros
                    reg.update({"erro": "%s: %s" % (type(e).__name__, e)})
                    if ano == hoje.year:
                        falhas.append("%s %d: %s" % (sigla, ano, reg["erro"]))
                entrada["anos"][str(ano)] = reg

        corrente = entrada["anos"].get(str(hoje.year), {})
        entrada["status"] = _status(motor, corrente, sigla)
        if motor is not None and motor.parcial:
            entrada["observacao"] = motor.parcial
        if motor is None and sigla in INCOMPATIVEIS:
            entrada["observacao"] = AVISO_INCOMPATIVEL
            entrada["motivo"] = INCOMPATIVEIS[sigla]
        cobertura["tribunais"][sigla] = entrada

    _gravar_json(caminho_cob, cobertura)
    return {"cobertura": cobertura, "falhas": falhas}


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--so", help="sigla de um tribunal")
    p.add_argument("--grupo", choices=["geral", "brasil"], help="geral = GitHub; brasil = exige IP brasileiro")
    p.add_argument("--falhar-se-erro", action="store_true", help="saída 1 se algum motor falhar")
    args = p.parse_args(argv)
    r = executar(RAIZ, descobrir(), datetime.date.today(), Cliente(), so=args.so, grupo=args.grupo)
    for f in r["falhas"]:
        print("FALHOU:", f, file=sys.stderr)
    contagem: Dict[str, int] = {}
    for t in r["cobertura"]["tribunais"].values():
        contagem[t["status"]] = contagem.get(t["status"], 0) + 1
    print("cobertura:", contagem)
    return 1 if (r["falhas"] and args.falhar_se_erro) else 0


if __name__ == "__main__":
    sys.exit(main())

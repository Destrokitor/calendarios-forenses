"""Modelo de motor. Copie para robo/motores/<sigla>.py e preencha. Apague este docstring.

Regras:
  - só LER a fonte e devolver o calendário; gravar e validar é do robô;
  - sem IA, sem rede fora de `rede.baixar(url)`;
  - levantar `AindaNaoPublicado` quando o ano pedido ainda não saiu;
  - qualquer dúvida sobre o EFEITO JURÍDICO de um dia: comentário `# DUVIDA:` e avise a revisão.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict

from ..modelo import calendario_vazio, dia, normalizar_local
from ..rede import Cliente
from .base import AindaNaoPublicado, Motor


class MotorEXEMPLO(Motor):
    sigla = "TJXX"
    precisa_ip_brasil = False  # True se bloquear o GitHub (descobrir testando com a sonda)
    parcial = ""               # descreva se a cobertura for sabidamente incompleta
    esperado = {
        "min_geral": 10,
        "min_locais": 1,
        "ancoras": {},         # {"2026-10-28": "Dia do Servidor"}: conferidas à mão
        "exige_recesso": True,
    }

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        cal = calendario_vazio(self.sigla, ano)
        # corpo = rede.baixar("https://...")
        # ... ler, e para cada dia: cal["geral"].append(dia(data, "sem_expediente", motivo, "id-da-fonte"))
        # ... locais: cal["locais"][normalizar_local("Nome")] = [dia(...), ...]
        raise NotImplementedError


MOTOR = MotorEXEMPLO()

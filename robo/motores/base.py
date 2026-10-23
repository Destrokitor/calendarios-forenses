"""Interface de um motor: o que cada tribunal precisa implementar.

Um motor sabe LER uma fonte oficial e devolver o calendário no formato de modelo.py. Ele
não grava arquivo, não valida e não decide nada sobre cobertura: isso é do robô
(executar.py), igual para todos. Assim o trabalho por tribunal fica só na leitura.

Para criar um motor: copie docs/MOTOR_MODELO.py para robo/motores/<sigla>.py, preencha a
ficha em docs/fichas/<SIGLA>.md e escreva os testes em tests/. Ver docs/PROCESSO_MOTORES.md.
"""
from __future__ import annotations

import datetime
from typing import Any, Dict, List

from ..rede import Cliente


class AindaNaoPublicado(Exception):
    """O tribunal ainda não publicou o calendário deste ano (ex.: ano que vem em outubro).

    Não é falha: o robô só registra o fato e tenta de novo no dia seguinte."""


class Motor:
    sigla = ""                   # ex.: "TJSP" (igual a registro.py)
    roda_na_nuvem = True         # False se a fonte bloqueia IP de nuvem: só roda no Mac
    parcial = ""                 # texto, se a cobertura for sabidamente incompleta
    esperado: Dict[str, Any] = {"min_geral": 1}   # ver validacao.validar

    def anos(self, hoje: datetime.date) -> List[int]:
        """Anos a coletar. Padrão: o ano corrente e o próximo (o próximo costuma sair
        no fim do ano anterior; se ainda não saiu, levantar AindaNaoPublicado)."""
        return [hoje.year, hoje.year + 1]

    def coletar(self, ano: int, rede: Cliente) -> Dict[str, Any]:
        raise NotImplementedError

"""Testes do motor do TJDFT. Só usam a FIXTURE (tests/fixtures/tjdft), nunca a rede.

A fixture feriados_e_expedientes_suspensos.html é a tabela da página do tribunal, guardada em
23/10/2026 (ver docs/fichas/TJDFT.md).
"""
from __future__ import annotations

import datetime
import os
import unittest

from robo import validacao
from robo.modelo import TIPOS, todos_os_dias
from robo.motores import tjdft
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjdft")


def _ler(nome: str) -> bytes:
    with open(os.path.join(FIX, nome), "rb") as f:
        return f.read()


class TestTJDFT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = tjdft.MOTOR
        cls.cal = tjdft.interpretar(_ler("feriados_e_expedientes_suspensos.html"), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJDFT", 2026, self.motor.esperado), [])

    def test_contagem_minima_e_um_so_local(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 43)  # 43 linhas de dia na tabela de 2026
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertEqual(list(self.cal["locais"]), ["DISTRITO FEDERAL"])
        self.assertEqual(self.cal["locais"]["DISTRITO FEDERAL"], [])

    def test_ancoras(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        self.assertIn("CONFRATERNIZAÇÃO", self.geral["2026-01-01"]["motivo"])
        self.assertIn("FERIADO FORENSE", self.geral["2026-02-16"]["motivo"])
        self.assertIn("DIA DO SERVIDOR", self.geral["2026-10-30"]["motivo"])
        self.assertIn("PORTARIA CONJUNTA 105/2025", self.geral["2026-04-20"]["motivo"])

    def test_recesso_de_janeiro_e_de_dezembro(self) -> None:
        for n in range(2, 7):
            self.assertEqual(self.geral["2026-01-%02d" % n]["tipo"], "recesso")
        self.assertNotIn("2026-01-07", self.geral)
        for n in (20, 21, 22, 23, 26, 27, 28, 29, 30):
            self.assertEqual(self.geral["2026-12-%02d" % n]["tipo"], "recesso")
        # 24, 25 e 31/12 aparecem como véspera/Natal/Ano Novo: não são recesso
        for n in (24, 25, 31):
            self.assertEqual(self.geral["2026-12-%02d" % n]["tipo"], "sem_expediente")

    def test_pontos_facultativos_viram_sem_expediente_e_nunca_suspensao(self) -> None:
        for data in ("2026-04-20", "2026-06-05", "2026-06-29", "2026-08-10", "2026-12-07"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente", data)
        self.assertNotIn("suspensao_prazo", {d["tipo"] for d in self.cal["geral"]})

    def test_quarta_de_cinzas_nao_e_parcial_no_calendario_judicial(self) -> None:
        # 18/02 só tem hora-limite no calendário dos cartórios (art. 3º da portaria): aqui é feriado
        self.assertEqual(self.geral["2026-02-18"]["tipo"], "sem_expediente")
        self.assertNotIn("horario", self.geral["2026-02-18"])
        self.assertFalse([d for d in self.cal["geral"] if d["tipo"] == "parcial"])

    def test_suspensao_posterior_entra_com_a_portaria_de_origem(self) -> None:
        self.assertIn("PORTARIA CONJUNTA 48/2026", self.geral["2026-06-29"]["motivo"])

    def test_todo_dia_tem_tipo_fonte_e_motivo(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        for d in todos_os_dias(self.cal):
            self.assertIn(d["tipo"], TIPOS)
            self.assertTrue(d["motivo"])
            self.assertIn(d["fonte"], ids)

    def test_ano_sem_dias_na_tabela_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            tjdft.interpretar(_ler("feriados_e_expedientes_suspensos.html"), 2027)

    def test_pagina_sem_a_tabela_e_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjdft.interpretar(b"<html><body>manutencao</body></html>", 2026)


if __name__ == "__main__":
    unittest.main()

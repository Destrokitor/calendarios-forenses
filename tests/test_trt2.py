"""Testes do motor do TRT2. Só usam a FIXTURE (tests/fixtures/trt2/feriados-suspensoes-2026.html), nunca a rede.

A fixture é a página "Feriados e Suspensões de Expediente" do portal, baixada em 23/10/2026
(ver docs/fichas/TRT2.md).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.motores import trt2
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trt2", "feriados-suspensoes-2026.html")


def _ler_fixture() -> bytes:
    with open(FIX, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt2.URL:
            return _ler_fixture()
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTRT2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt2.MOTOR
        cls.cal = trt2.interpretar(_ler_fixture(), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT2", 2026, self.motor.esperado), [])

    def test_contagem_minima(self) -> None:
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertGreaterEqual(len(self.cal["locais"]), self.motor.esperado["min_locais"])

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt2.URL])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], self.cal["locais"])

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)

    def test_recesso_janeiro_e_dezembro(self) -> None:
        self.assertEqual(self.geral["2026-01-01"]["tipo"], "recesso")
        self.assertEqual(self.geral["2026-12-31"]["tipo"], "recesso")
        # 07 a 20/01 não aparecem na grade: não podem ser inventados
        for dia in range(7, 21):
            self.assertNotIn("2026-01-%02d" % dia, self.geral)

    def test_suspensao_de_prazo_so_onde_a_fonte_diz(self) -> None:
        for data in ("2026-01-21", "2026-01-22", "2026-01-23"):
            self.assertEqual(self.geral[data]["tipo"], "suspensao_prazo", data)
        suspensoes = [d for d in self.cal["geral"] if d["tipo"] == "suspensao_prazo"]
        self.assertEqual(len(suspensoes), 3)

    def test_suspensao_de_expediente_vira_sem_expediente(self) -> None:
        for data in ("2026-04-20", "2026-06-05", "2026-07-10", "2026-08-10", "2026-12-07"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente", data)

    def test_18_02_fica_de_fora_sem_decisao(self) -> None:
        # DUVIDA registrada no motor: Quarta de Cinzas sem decisão de efeito
        self.assertNotIn("2026-02-18", self.geral)
        self.assertNotIn("2026-02-18", {d["data"] for lista in self.cal["locais"].values() for d in lista if d["motivo"].startswith("Suspensão")})

    def test_orgao_especifico_nao_vai_em_geral_nem_em_local(self) -> None:
        # 13/07: Fórum Trabalhista de Cubatão (Portaria n. 17/GP.CR). Efeito fica no detalhe do dia.
        self.assertNotIn("2026-07-13", self.geral)
        self.assertNotIn("2026-07-13", {d["data"] for d in self.cal["locais"].get("CUBATÃO", [])})
        for data in ("2026-02-03", "2026-03-20", "2026-08-21", "2026-09-14"):
            self.assertNotIn(data, self.geral, data)

    def test_feriado_municipal_so_no_local(self) -> None:
        # Corpus Christi (04/06): 31 municípios, nunca em geral
        self.assertNotIn("2026-06-04", self.geral)
        self.assertIn("SÃO PAULO", self.cal["locais"])
        corpus = [d for d in self.cal["locais"]["SÃO PAULO"] if d["data"] == "2026-06-04"]
        self.assertEqual(len(corpus), 1)
        self.assertEqual(corpus[0]["tipo"], "sem_expediente")

    def test_local_com_mais_de_um_evento(self) -> None:
        # Cubatão: aniversário (09/04), Corpus Christi (04/06) e feriado religioso (15/08)
        datas = [d["data"] for d in self.cal["locais"]["CUBATÃO"]]
        self.assertEqual(datas, ["2026-04-09", "2026-06-04", "2026-08-15"])

    def test_dia_com_geral_e_local_na_mesma_data(self) -> None:
        # 22/01: suspensão de prazo em geral e aniversário de São Vicente no local
        self.assertEqual(self.geral["2026-01-22"]["tipo"], "suspensao_prazo")
        self.assertIn("2026-01-22", {d["data"] for d in self.cal["locais"]["SÃO VICENTE"]})

    def test_ano_sem_dias_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt2.interpretar(_ler_fixture(), 2027)

    def test_pagina_sem_eventos_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt2.interpretar(b"<html><body>manutencao</body></html>", 2026)


if __name__ == "__main__":
    unittest.main()

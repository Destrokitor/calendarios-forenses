"""Testes do motor do TRT24. Só usam a FIXTURE (tests/fixtures/trt24/calendario.html), nunca a rede.

A fixture é a página do calendário do portal, guardada em 23/10/2026 (ver docs/fichas/TRT24.md).
"""
from __future__ import annotations

import os
import re
import unittest

from robo import validacao
from robo.modelo import normalizar_local
from robo.motores import trt24
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trt24", "calendario.html")


def _ler_fixture() -> bytes:
    with open(FIX, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt24.URL:
            return _ler_fixture()
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTRT24(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt24.MOTOR
        cls.conteudo = _ler_fixture()
        cls.cal = trt24.interpretar(cls.conteudo, 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT24", 2026, self.motor.esperado), [])

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt24.URL])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], self.cal["locais"])

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        # 16 e 17/02: Carnaval (Nacional), feriado de sem expediente
        for data in ("2026-02-16", "2026-02-17"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente")
            self.assertEqual(self.geral[data]["motivo"], "Carnaval")
        # 18/02: Suspensão expediente até as 13h (RA 92/2025), parcial
        self.assertEqual(self.geral["2026-02-18"]["tipo"], "parcial")
        self.assertEqual(self.geral["2026-02-18"]["horario"], "até as 13h")
        # 24/06 e 29/06: expediente encurtado por RA 79/2026 e RA 81/2026
        self.assertEqual(self.geral["2026-06-24"]["tipo"], "parcial")
        self.assertEqual(self.geral["2026-06-24"]["horario"], "das 8h às 15h")
        self.assertEqual(self.geral["2026-06-29"]["tipo"], "parcial")
        self.assertEqual(self.geral["2026-06-29"]["horario"], "das 7h às 11h")

    def test_suspensao_de_expediente_sem_horario_e_sem_expediente(self) -> None:
        for data in ("2026-04-20", "2026-06-05", "2026-08-10", "2026-12-07"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente", data)
            self.assertNotIn("horario", self.geral[data])

    def test_recesso_janeiro_e_dezembro(self) -> None:
        # 01/01 e 25/12 têm duas linhas (feriado nacional + recesso do tribunal): conta as duas
        tipos = {}
        for d in self.cal["geral"]:
            tipos.setdefault(d["data"], set()).add(d["tipo"])
        for n in range(1, 7):
            self.assertIn("recesso", tipos["2026-01-%02d" % n])
        for n in range(20, 32):
            self.assertIn("recesso", tipos["2026-12-%02d" % n])
        self.assertIn("sem_expediente", tipos["2026-01-01"])  # Confraternização Universal
        self.assertIn("sem_expediente", tipos["2026-12-25"])  # Natal
        # 07 a 20/01 não são listados na fonte: o motor não inventa
        for n in range(7, 21):
            self.assertNotIn("2026-01-%02d" % n, self.geral)

    def test_contagem_minima(self) -> None:
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertEqual(len(self.cal["locais"]), self.motor.esperado["min_locais"])  # 22 municípios
        # a fixture tem 94 linhas de dados em 2026 (46 gerais + 48 locais), ver a ficha
        self.assertEqual(len(self.cal["geral"]) + sum(len(v) for v in self.cal["locais"].values()), 94)

    def test_locais_sao_os_22_do_seletor_e_nomes_normalizados(self) -> None:
        for nome in self.cal["locais"]:
            self.assertEqual(nome, normalizar_local(nome))
        for nome in ("AMAMBAI", "CAMPO GRANDE", "CORUMBÁ", "COXIM", "MUNDO NOVO", "SIDROLÂNDIA",
                     "SÃO GABRIEL DO OESTE", "TRÊS LAGOAS", "RIO BRILHANTE"):
            self.assertIn(nome, self.cal["locais"])
        self.assertNotIn("TODAS AS CIDADES.", self.cal["locais"])

    def test_local_campo_grande_suspensao_de_prazo(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["CAMPO GRANDE"]}
        for data in ("2026-09-10", "2026-09-11"):
            self.assertEqual(dias[data]["tipo"], "suspensao_prazo", data)
            self.assertEqual(dias[data]["motivo"], "Suspensão de prazos processuais")
        # suspensão de prazo local NÃO vira geral
        self.assertNotIn("2026-09-10", self.geral)

    def test_local_mundo_novo_remarcado(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["MUNDO NOVO"]}
        self.assertEqual(dias["2026-05-11"]["tipo"], "sem_expediente")
        self.assertIn("Remarcado", dias["2026-05-11"]["motivo"])
        self.assertNotIn("2026-05-11", self.geral)

    def test_local_corumba_padroeiro(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["CORUMBÁ"]}
        self.assertEqual(dias["2026-02-02"]["tipo"], "sem_expediente")
        self.assertEqual(dias["2026-02-02"]["motivo"], "Padroeiro de Corumbá")

    def test_dia_do_servidor_remarcado_vale_para_o_tribunal(self) -> None:
        self.assertEqual(self.geral["2026-10-30"]["tipo"], "sem_expediente")
        self.assertIn("Remarcado", self.geral["2026-10-30"]["motivo"])

    def test_todo_dia_tem_fonte_valida(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        todos = list(self.cal["geral"]) + [d for v in self.cal["locais"].values() for d in v]
        self.assertTrue(todos)
        for d in todos:
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])

    def test_dia_parcial_tem_horario(self) -> None:
        for d in self.cal["geral"]:
            if d["tipo"] == "parcial":
                self.assertTrue(d.get("horario"), d)
                self.assertTrue(re.match(r"(até|das) ", d["horario"]), d)

    def test_ano_sem_dias_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt24.interpretar(self.conteudo, 2027)

    def test_pagina_sem_tabela_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt24.interpretar(b"<html><body>manutencao</body></html>", 2026)


if __name__ == "__main__":
    unittest.main()

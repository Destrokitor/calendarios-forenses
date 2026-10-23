"""Testes do motor do TRT11. Só usam as FIXTURES (tests/fixtures/trt11/), nunca a rede.

As fixtures são a página de suspensões do portal (página 1 da lista) e a página do evento 690
(suspensão dos prazos de 07 a 20/01/2026), guardadas em 23/10/2026 (ver docs/fichas/TRT11.md).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.motores import trt11
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

PASTA = os.path.join(os.path.dirname(__file__), "fixtures", "trt11")
LISTA = os.path.join(PASTA, "calendario-suspensao-lista.html")
EVENTO_690 = os.path.join(PASTA, "evento-690.html")
URL_690 = trt11.URL_BASE + "/index.php/sociedades/calendarios/calendario-susp/690-suspensao-dos-prazos-audiencias-e-sessoes-3"


def _ler(caminho: str) -> bytes:
    with open(caminho, "rb") as f:
        return f.read()


def _conteudo() -> dict:
    return {"listas": [_ler(LISTA)], "detalhes": {URL_690: _ler(EVENTO_690)}}


class RedeFalsa:
    """Responde com as fixtures no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt11.URL_LISTA:
            return _ler(LISTA)
        if url == URL_690:
            return _ler(EVENTO_690)
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTRT11(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt11.MOTOR
        cls.cal = trt11.interpretar(_conteudo(), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT11", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral, data)
        self.assertEqual(self.geral["2026-01-07"][0]["tipo"], "suspensao_prazo")
        self.assertEqual(self.geral["2026-01-20"][0]["tipo"], "suspensao_prazo")
        for data in ("2026-04-20", "2026-06-05", "2026-08-10"):
            self.assertEqual(self.geral[data][0]["tipo"], "sem_expediente", data)
            self.assertIn("322/2025", self.geral[data][0]["motivo"])

    def test_periodo_de_prazos_vira_um_dia_por_data(self) -> None:
        prazos = [d for d in self.cal["geral"] if d["tipo"] == "suspensao_prazo"]
        datas = [d["data"] for d in prazos]
        self.assertEqual(datas, ["2026-01-%02d" % n for n in range(7, 21)])  # 14 datas, sem buraco
        self.assertEqual(len(set(datas)), len(datas))
        for d in prazos:
            self.assertEqual(d["fonte"], "suspensoes")
            self.assertNotIn("horario", d)

    def test_expediente_nao_vira_suspensao_de_prazo(self) -> None:
        for data in ("2026-04-20", "2026-06-05", "2026-08-10"):
            self.assertEqual([d["tipo"] for d in self.geral[data]], ["sem_expediente"])

    def test_nada_fora_do_ano_pedido(self) -> None:
        # os eventos de 2025 e anos anteriores da fixture não entram em 2026
        for d in self.cal["geral"]:
            self.assertTrue(d["data"].startswith("2026-"), d)
        self.assertNotIn("2025-11-21", self.geral)
        self.assertNotIn("2025-06-20", self.geral)

    def test_sem_locais_e_sem_recesso(self) -> None:
        self.assertEqual(self.cal["locais"], {})
        self.assertFalse(any(d["tipo"] == "recesso" for d in self.cal["geral"]))
        self.assertFalse(self.motor.esperado["exige_recesso"])

    def test_contagem_minima(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 17)
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt11.URL_LISTA, URL_690])
        self.assertEqual(cal["geral"], self.cal["geral"])

    def test_ano_sem_eventos_nao_e_falha(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt11.interpretar(_conteudo(), 2027)

    def test_pagina_do_prazo_ausente_levanta_erro(self) -> None:
        conteudo = {"listas": [_ler(LISTA)], "detalhes": {}}
        with self.assertRaises(ErroDeFonte):
            trt11.interpretar(conteudo, 2026)

    def test_parcial_declara_o_que_fica_de_fora(self) -> None:
        texto = self.motor.parcial
        for trecho in ("feriados", "PDF", "robots", "29/06", "Varas", "RA 322/2025"):
            self.assertIn(trecho, texto)


if __name__ == "__main__":
    unittest.main()

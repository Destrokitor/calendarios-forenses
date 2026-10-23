"""Testes do motor do TJSC. Só usam a FIXTURE (tests/fixtures/tjsc), nunca a rede.

A fixture é a resposta do endpoint JSON da busca textual do TJSC para a Resolução GP n. 1/2026
(calendário de feriados para efeitos forenses).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.motores import tjsc
from robo.motores.base import AindaNaoPublicado

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjsc")
ARQUIVO = "resolucao-gp-1-2026-integra.json"


def _ler_fixture() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjsc.ATOS[2026]:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_fixture()


class TestTJSC(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = tjsc.MOTOR
        cls.cal = tjsc.interpretar(_ler_fixture(), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJSC", 2026, self.motor.esperado), [])

    def test_contagem_lida(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 16)
        self.assertEqual(len(self.cal["locais"]), 110)
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
            self.assertEqual(self.geral[data][0]["tipo"], "sem_expediente", nome)
        self.assertEqual(self.geral["2026-02-16"][0]["motivo"], "Segunda-feira de Carnaval")
        self.assertEqual(self.geral["2026-06-04"][0]["motivo"], "Corpus Christi")
        self.assertEqual(self.geral["2026-12-08"][0]["motivo"], "Dia da Justiça")

    def test_todo_dia_tem_fonte_registrada(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        for d in self.cal["geral"]:
            self.assertIn(d["fonte"], ids)
        for lista in self.cal["locais"].values():
            for d in lista:
                self.assertIn(d["fonte"], ids)

    def test_local_municipal(self) -> None:
        # 09/03: Dia do Município de Joinville, só a comarca de Joinville (ficha, âncora 5).
        self.assertEqual(self.cal["locais"]["JOINVILLE"][0]["data"], "2026-03-09")
        self.assertEqual(self.cal["locais"]["JOINVILLE"][0]["tipo"], "sem_expediente")
        self.assertNotIn("2026-03-09", self.geral)

    def test_capital_entra_so_em_florianopolis(self) -> None:
        # 23/03: "Tribunal de Justiça, Turmas Recursais e a comarca da Capital" (ficha, âncora 5).
        datas = [d["data"] for d in self.cal["locais"]["FLORIANÓPOLIS"]]
        self.assertIn("2026-03-23", datas)
        self.assertNotIn("2026-03-23", self.geral)

    def test_local_com_duas_datas_no_mesmo_dia_sem_repetir(self) -> None:
        # 08/12 tem o geral (Dia da Justiça) e vários municípios; cada um fica na sua lista.
        self.assertIn("2026-12-08", self.geral)
        self.assertEqual(self.cal["locais"]["ITAPEMA"][-1]["data"], "2026-12-08")

    def test_sem_recesso_e_sem_suspensao(self) -> None:
        # O recesso não está no ato (Art. 1º, parágrafo único): nenhum dia de recesso, nenhum parcial.
        tipos = {d["tipo"] for d in self.cal["geral"]}
        self.assertEqual(tipos, {"sem_expediente"})
        for lista in self.cal["locais"].values():
            self.assertTrue(all(d["tipo"] == "sem_expediente" for d in lista))

    def test_ano_diferente_do_ato_e_falha(self) -> None:
        with self.assertRaises(tjsc.ErroDeFonte):
            tjsc.interpretar(_ler_fixture(), 2027)

    def test_ano_sem_ato_conhecido_nao_e_falha(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])

    def test_coleta_com_rede_falsa(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjsc.ATOS[2026]])
        self.assertEqual(validacao.validar(cal, "TJSC", 2026, self.motor.esperado), [])


if __name__ == "__main__":
    unittest.main()

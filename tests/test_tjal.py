"""Testes do motor do TJAL. Só usam as FIXTURES (tests/fixtures/tjal), nunca a rede.

As fixtures são os dois atos normativos do TJAL, em JSON da API do portal (campo `texto` em HTML).
"""
from __future__ import annotations

import json
import os
import unittest

from robo import validacao
from robo.motores import tjal
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjal")
ATO_03 = os.path.join(FIX, "ato_normativo_03_2026_detalhes.json")
ATO_22 = os.path.join(FIX, "ato_normativo_22_2025_detalhes.json")


def _ler(caminho):
    with open(caminho, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com as fixtures no lugar da internet."""

    def __init__(self):
        self.pedidos = []

    def baixar(self, url):
        self.pedidos.append(url)
        if url == tjal.URL_ATO_03_2026:
            return _ler(ATO_03)
        if url == tjal.URL_ATO_22_2025:
            return _ler(ATO_22)
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTJAL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ato03 = json.loads(_ler(ATO_03).decode("utf-8"))
        cls.ato22 = json.loads(_ler(ATO_22).decode("utf-8"))
        cls.motor = tjal.MOTOR
        cls.cal = tjal.interpretar(cls.ato03, cls.ato22, 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self):
        self.assertEqual(validacao.validar(self.cal, "TJAL", 2026, self.motor.esperado), [])

    def test_ancoras(self):
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        for data in ("2026-04-20", "2026-06-05", "2026-08-10", "2026-12-07", "2026-01-02"):
            self.assertEqual(self.geral[data]["tipo"], "suspensao_prazo", data)
        self.assertIn("Tiradentes", self.geral["2026-04-20"]["motivo"])
        self.assertIn("Corpus Christi", self.geral["2026-06-05"]["motivo"])
        self.assertIn("Dia do Jurista", self.geral["2026-08-10"]["motivo"])
        self.assertIn("Dia da Justiça", self.geral["2026-12-07"]["motivo"])

    def test_contagem_e_locais(self):
        self.assertEqual(len(self.cal["geral"]), 9)  # 5 suspensões + 4 dias de recesso
        self.assertEqual(self.cal["locais"], {})

    def test_recesso_de_janeiro(self):
        recesso = sorted(d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso")
        self.assertEqual(recesso, ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"])

    def test_suspensao_municipal_fica_de_fora(self):
        # 28/08 (art. 4º): só vale nos municípios que preveem o feriado; o ato não diz quais.
        self.assertNotIn("2026-08-28", self.geral)
        self.assertIn("28/08", self.motor.parcial)
        self.assertIn("municípios", self.motor.parcial)

    def test_nao_inventa_feriados_de_outras_fontes(self):
        # Feriados nacionais/estaduais e municipais não estão nos atos: não podem aparecer.
        for data in ("2026-04-21", "2026-09-07", "2026-10-12", "2026-11-02", "2026-11-15"):
            self.assertNotIn(data, self.geral, data)

    def test_fontes_e_tipos_validos(self):
        ids = {f["id"] for f in self.cal["fontes"]}
        self.assertEqual(ids, {"ato03", "ato22"})
        for d in self.cal["geral"]:
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])
            self.assertNotIn("horario", d)

    def test_coletar_baixa_os_dois_atos_e_valida(self):
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjal.URL_ATO_03_2026, tjal.URL_ATO_22_2025])
        self.assertEqual(validacao.validar(cal, "TJAL", 2026, self.motor.esperado), [])

    def test_ano_seguinte_ainda_nao_publicado(self):
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])

    def test_ato_com_artigo_alterado_e_recusado(self):
        alterado = dict(self.ato03)
        alterado["texto"] = self.ato03["texto"].replace("Art. 5º Suspender", "Art. 5º Revogado")
        self.assertNotEqual(alterado["texto"], self.ato03["texto"])
        with self.assertRaises(ErroDeFonte):
            tjal.interpretar(alterado, self.ato22, 2026)

    def test_ano_errado_e_recusado(self):
        with self.assertRaises(ErroDeFonte):
            tjal.interpretar(self.ato03, self.ato22, 2027)

    def test_json_sem_texto_e_recusado(self):
        sem_texto = {k: v for k, v in self.ato22.items() if k != "texto"}
        with self.assertRaises(ErroDeFonte):
            tjal.interpretar(self.ato03, sem_texto, 2026)


if __name__ == "__main__":
    unittest.main()

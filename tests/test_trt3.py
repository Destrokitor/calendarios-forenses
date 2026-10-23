"""Testes do motor do TRT3. Só usam as FIXTURES (tests/fixtures/trt3/), nunca a rede.

As fixtures são as duas páginas HTML do portal, guardadas em 23/10/2026 (ver docs/fichas/TRT3.md).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.modelo import normalizar_local
from robo.motores import trt3
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

PASTA = os.path.join(os.path.dirname(__file__), "fixtures", "trt3")
GERAL = os.path.join(PASTA, "calendario-2026.html")
LOCAIS = os.path.join(PASTA, "feriados-locais-2026.html")


def _ler(caminho: str) -> bytes:
    with open(caminho, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com as fixtures no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt3.URL_GERAL_2026:
            return _ler(GERAL)
        if url == trt3.URL_LOCAIS_2026:
            return _ler(LOCAIS)
        raise AssertionError("URL fora das fixtures: %s" % url)


class TestTRT3(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt3.MOTOR
        cls.geral_bytes = _ler(GERAL)
        cls.locais_bytes = _ler(LOCAIS)
        cls.cal = trt3.interpretar(cls.geral_bytes, cls.locais_bytes, 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def _tipos(self, data: str) -> set:
        return {d["tipo"] for d in self.geral.get(data, [])}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT3", 2026, self.motor.esperado), [])

    def test_coletar_pede_as_duas_paginas_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt3.URL_GERAL_2026, trt3.URL_LOCAIS_2026])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], self.cal["locais"])

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        self.assertEqual(self._tipos("2026-02-16"), {"sem_expediente"})
        self.assertEqual(self._tipos("2026-02-17"), {"sem_expediente"})
        self.assertEqual(self.geral["2026-02-16"][0]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-02-18"][0]["motivo"], "Cinzas")
        self.assertEqual(self.geral["2026-04-21"][0]["motivo"], "Tiradentes")
        self.assertEqual(self.geral["2026-08-14"][0]["motivo"].split(",")[0],
                         "Dia da Criação dos Cursos Jurídicos")
        self.assertIn("Dia do Servidor", self.geral["2026-10-30"][0]["motivo"])
        self.assertEqual(self.geral["2026-12-08"][0]["motivo"], "Dia da Justiça")

    def test_recesso_janeiro_e_dezembro_sem_chave_por_data(self) -> None:
        # 01/01 e 25/12 têm duas linhas cada (feriado + recesso): as duas contam
        self.assertEqual(self._tipos("2026-01-01"), {"sem_expediente", "recesso"})
        self.assertEqual(self._tipos("2026-12-25"), {"sem_expediente", "recesso"})
        for n in range(1, 7):
            self.assertIn("recesso", self._tipos("2026-01-%02d" % n))
        for n in range(20, 32):
            self.assertIn("recesso", self._tipos("2026-12-%02d" % n))
        # 07 a 19/01 não estão na tabela: o motor não inventa
        for n in range(7, 20):
            self.assertNotIn("2026-01-%02d" % n, self.geral)

    def test_semana_santa_e_dia_do_trabalhador(self) -> None:
        for n in range(1, 6):
            data = "2026-04-%02d" % n
            self.assertEqual(self.geral[data][0]["motivo"], "Semana Santa", data)
            self.assertEqual(self._tipos(data), {"sem_expediente"})
        self.assertEqual(self.geral["2026-05-01"][0]["motivo"], "Dia do Trabalhador")
        self.assertEqual(self.geral["2026-05-01"][0]["fonte"], trt3.FONTE_RA)

    def test_corpus_christi_e_suspensao_de_5_fora_do_geral(self) -> None:
        self.assertNotIn("2026-06-04", self.geral)
        self.assertNotIn("2026-06-05", self.geral)
        bh = {d["data"]: d for d in self.cal["locais"]["BELO HORIZONTE"]}
        self.assertEqual(bh["2026-06-04"]["tipo"], "sem_expediente")
        self.assertIn("Corpus Christi", bh["2026-06-04"]["motivo"])
        self.assertEqual(bh["2026-06-05"]["motivo"], "Suspensão do expediente (RA 109/2025)")

    def test_suspensao_de_5_so_em_locais_e_so_nos_municipios_listados(self) -> None:
        # a tabela lista a suspensão de 05/06 em todos os 66 municípios: cada um tem o seu registro
        for nome, dias in self.cal["locais"].items():
            datas = [d["data"] for d in dias]
            self.assertIn("2026-06-05", datas, nome)
        # e nenhum deles vale para o tribunal inteiro
        self.assertNotIn("2026-06-05", self.geral)

    def test_locais_ancoras(self) -> None:
        self.assertIn("2026-01-15", {d["data"] for d in self.cal["locais"]["UNAÍ"]})
        self.assertIn("2026-03-27", {d["data"] for d in self.cal["locais"]["CONTAGEM"]})
        almenara = {d["data"]: d for d in self.cal["locais"]["ALMENARA"]}
        self.assertIn("2026-01-12", almenara)  # transferido de 13/01 para 12/01
        self.assertIn("transferido", almenara["2026-01-12"]["motivo"])
        self.assertIn("2026-09-21", {d["data"] for d in self.cal["locais"]["AIMORÉS"]})

    def test_locais_sao_66_e_nomes_normalizados(self) -> None:
        self.assertEqual(len(self.cal["locais"]), self.motor.esperado["min_locais"])
        for nome in self.cal["locais"]:
            self.assertEqual(nome, normalizar_local(nome))
        self.assertIn("SÃO JOÃO DEL REI", self.cal["locais"])
        self.assertIn("UBERLÂNDIA", self.cal["locais"])
        self.assertNotIn("TOTAL", self.cal["locais"])

    def test_todo_dia_tem_fonte_valida_e_motivo(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        todos = list(self.cal["geral"]) + [d for v in self.cal["locais"].values() for d in v]
        self.assertTrue(todos)
        for d in todos:
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_contagem_exata_lida(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 40)
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 274)

    def test_ano_fora_do_mapa_levanta_ainda_nao_publicado(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])

    def test_pagina_que_nao_e_do_ano_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt3.interpretar(self.geral_bytes, self.locais_bytes, 2027)

    def test_1_de_maio_some_da_pagina_levanta_erro_de_fonte(self) -> None:
        trocada = self.geral_bytes.replace("Dia do Trabalhador".encode("utf-8"), b"Outro")
        with self.assertRaises(ErroDeFonte):
            trt3.interpretar(trocada, self.locais_bytes, 2026)

    def test_pagina_sem_tabela_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt3.interpretar(b"<html><body>manutencao</body></html>", b"<html></html>", 2026)


if __name__ == "__main__":
    unittest.main()

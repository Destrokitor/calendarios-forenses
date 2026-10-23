"""Testes do motor do TRT19. Só usam a FIXTURE (tests/fixtures/trt19/ato_170_2025_feriados_2026.pdf),
nunca a rede. O texto de referência é o .txt ao lado (pdftotext -layout).

A fixture é o Ato nº 170/GP/TRT 19ª, de 29/09/2025 (ver docs/fichas/TRT19.md).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.motores import trt19
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trt19", "ato_170_2025_feriados_2026.pdf")


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt19.URL:
            with open(FIX, "rb") as f:
                return f.read()
        raise AssertionError("URL fora da fixture: %s" % url)


@unittest.skipUnless(shutil.which("pdftotext"), "pdftotext não instalado")
class TestTRT19(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt19.MOTOR
        with open(FIX, "rb") as f:
            cls.pdf = f.read()
        cls.cal = trt19.interpretar(trt19.pdf_para_texto(cls.pdf), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT19", 2026, self.motor.esperado), [])

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt19.URL])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], {})

    def test_ano_sem_ato_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())

    def test_ato_de_outro_exercicio_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt19.interpretar(trt19.pdf_para_texto(self.pdf), 2027)

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)

    def test_carnaval_cinzas_e_datas_com_dia_da_semana_certo(self) -> None:
        self.assertEqual(self.geral["2026-02-16"][0]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-02-17"][0]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-02-18"][0]["motivo"], "Cinzas")
        self.assertEqual(self.geral["2026-02-18"][0]["tipo"], "sem_expediente")

    def test_recesso_janeiro_e_dezembro(self) -> None:
        tipos = {}
        for d in self.cal["geral"]:
            tipos.setdefault(d["data"], set()).add(d["tipo"])
        for n in range(2, 7):
            self.assertEqual(tipos["2026-01-%02d" % n], {"recesso"})
        for n in range(20, 32):
            self.assertIn("recesso", tipos["2026-12-%02d" % n])
        self.assertEqual(sum(1 for d in self.cal["geral"] if d["tipo"] == "recesso"), 17)
        # 01/01 não é recesso: é feriado; 07 a 19/12 não são recesso
        self.assertEqual(tipos["2026-01-01"], {"sem_expediente"})
        self.assertNotIn("2026-01-07", tipos)

    def test_natal_tem_dois_registros(self) -> None:
        # 25/12 é Natal (feriado) e cai dentro do recesso: duas linhas, não se guarda por dicionário
        tipos = sorted(d["tipo"] for d in self.geral["2026-12-25"])
        self.assertEqual(tipos, ["recesso", "sem_expediente"])

    def test_contagem_minima_e_datas_unicas(self) -> None:
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertEqual(len(self.cal["geral"]), 39)   # 39 registros, 38 datas (25/12 duplicada)
        self.assertEqual(len(self.geral), 38)

    def test_intervalo_semana_santa_vira_um_dia_por_data(self) -> None:
        for data in ("2026-04-01", "2026-04-02", "2026-04-03"):
            self.assertEqual(self.geral[data][0]["motivo"], "Semana Santa")
            self.assertEqual(self.geral[data][0]["tipo"], "sem_expediente")

    def test_pontos_facultativos_nao_entram(self) -> None:
        # DUVIDA registrada no motor: o ato não diz se o ponto suspende prazo
        for data in ("2026-04-20", "2026-06-05", "2026-08-10", "2026-12-07"):
            self.assertNotIn(data, self.geral, data)

    def test_transferencia_dia_do_servidor_vale_para_o_tribunal(self) -> None:
        self.assertEqual(self.geral["2026-10-30"][0]["tipo"], "sem_expediente")
        self.assertIn("Dia do Servidor", self.geral["2026-10-30"][0]["motivo"])

    def test_descricao_com_continuacao_de_linha(self) -> None:
        self.assertEqual(self.geral["2026-08-11"][0]["motivo"],
                         "Criação dos Cursos Jurídicos, Dia da Magistratura, Dia do Advogado")
        self.assertIn("para efeitos forenses", self.geral["2026-12-08"][0]["motivo"])

    def test_locais_vazio_e_parcial_declarado(self) -> None:
        self.assertEqual(self.cal["locais"], {})
        self.assertTrue(self.motor.parcial)

    def test_todo_dia_tem_fonte_valida(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        for d in self.cal["geral"]:
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])

    def test_texto_sem_tabela_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt19.interpretar("PODER JUDICIÁRIO exercício de 2026 sem tabela", 2026)


if __name__ == "__main__":
    unittest.main()

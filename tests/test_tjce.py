"""Testes do motor do TJCE. Só usam a FIXTURE (tests/fixtures/tjce), nunca a rede.

A fixture é a Portaria nº 2924/2025 (DJE ed. 3690), com o Anexo Único (jan/2026 a jan/2027).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjce
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjce")
ARQUIVO = "portaria_2924_2025_feriados_2026.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjce.FONTE_URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJCE(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjce.MOTOR
        cls.cal = tjce.interpretar(tjce.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJCE", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        # Anexo Único, conferidas à mão contra o texto da fixture.
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertEqual(self.geral["2026-03-25"][0]["motivo"], "Data Magna")
        self.assertEqual(self.geral["2026-04-21"][0]["motivo"], "Tiradentes")
        self.assertEqual(self.geral["2026-12-08"][0]["motivo"], "Dia da Justiça")
        self.assertEqual(self.geral["2026-12-20"][0]["tipo"], "recesso")
        self.assertEqual(self.geral["2026-02-18"][0]["tipo"], "parcial")

    def test_contagem_lida(self) -> None:
        # 34 dias: 18 de recesso (01 a 06/01 e 20 a 31/12) + 16 de feriados e pontos.
        self.assertEqual(len(self.cal["geral"]), 34)
        self.assertEqual(self.cal["locais"], {})

    def test_recesso_natalino(self) -> None:
        recesso = sorted(d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso")
        self.assertEqual(len(recesso), 18)
        self.assertEqual(recesso[0], "2026-01-01")
        self.assertEqual(recesso[5], "2026-01-06")
        self.assertEqual(recesso[6], "2026-12-20")
        self.assertEqual(recesso[-1], "2026-12-31")

    def test_carnaval_e_cinzas(self) -> None:
        # 16 e 17: ponto facultativo (sem expediente). 18: parcial, expediente a partir das 14h.
        self.assertEqual(self.geral["2026-02-16"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-02-17"][0]["tipo"], "sem_expediente")
        dia18 = self.geral["2026-02-18"][0]
        self.assertEqual(dia18["tipo"], "parcial")
        self.assertIn("14h", dia18["horario"])

    def test_pontos_facultativos_como_sem_expediente(self) -> None:
        # São José, Semana Santa (02 e 03/04) e Corpus Christi são pontos: sem_expediente.
        self.assertEqual(self.geral["2026-03-19"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-04-02"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-04-03"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-06-04"][0]["tipo"], "sem_expediente")

    def test_meses_das_linhas_quebradas(self) -> None:
        # Conferidos à mão no anexo: o mês vem numa linha solta, por isso cada data é checada.
        esperadas = ["2026-05-01", "2026-09-07", "2026-10-12", "2026-10-28",
                     "2026-11-02", "2026-11-20", "2026-12-08"]
        for data in esperadas:
            self.assertIn(data, self.geral, data)

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjce.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_parcial_tem_horario(self) -> None:
        for d in todos_os_dias(self.cal):
            if d["tipo"] == "parcial":
                self.assertTrue(d.get("horario"))

    def test_ano_seguinte_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())

    def test_ano_fora_da_portaria_recusado_na_leitura(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjce.interpretar(tjce.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjce.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 34)


if __name__ == "__main__":
    unittest.main()

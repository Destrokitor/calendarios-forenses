"""Testes do motor do TJGO. Só usam a FIXTURE (tests/fixtures/tjgo), nunca a rede.

A fixture é a tabela "FERIADOS 2026" do TJGO (versão de 08/06/2026), 2 páginas.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjgo
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjgo")
ARQUIVO = "feriados_tjgo_2026_08062026.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjgo.FONTES[2026]:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJGO(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjgo.MOTOR
        cls.cal = tjgo.interpretar(tjgo.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJGO", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        # Âncoras 1 a 5 da ficha.
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertEqual(self.geral["2026-02-16"][0]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-02-16"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-02-18"][0]["tipo"], "parcial")
        self.assertEqual(self.geral["2026-02-18"][0]["horario"], "até 12h")
        self.assertEqual(self.geral["2026-04-01"][0]["motivo"], "Semana Santa")
        self.assertEqual(self.geral["2026-12-08"][0]["motivo"], "Dia da Justiça")
        self.assertEqual(self.geral["2026-12-20"][0]["tipo"], "recesso")

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 32)  # 20 feriados (incl. 18/02 parcial) + 12 de recesso
        self.assertEqual(len(self.cal["locais"]), 4)
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 4)

    def test_recesso_so_de_2026(self) -> None:
        recesso = sorted(d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso")
        self.assertEqual(recesso[0], "2026-12-20")
        self.assertEqual(recesso[-1], "2026-12-31")
        self.assertEqual(len(recesso), 12)  # 6/1/2027 não entra no calendário de 2026

    def test_pontos_facultativos_ficam_fora(self) -> None:
        # 20/03, 20/04 e 05/06 são pontos facultativos: não entram (ver DUVIDA no motor).
        for data in ("2026-03-20", "2026-04-20", "2026-06-05"):
            self.assertNotIn(data, self.geral)
            for lista in self.cal["locais"].values():
                self.assertNotIn(data, {d["data"] for d in lista})

    def test_feriado_municipal_so_nas_comarcas(self) -> None:
        # 24/05 é feriado só do Tribunal e das comarcas listadas: não vai para o geral.
        self.assertNotIn("2026-05-24", self.geral)
        for nome in ("GOIÂNIA", "IPORÁ", "LEOPOLDO DE BULHÕES", "SENADOR CANEDO"):
            dias = {d["data"]: d for d in self.cal["locais"][nome]}
            self.assertEqual(dias["2026-05-24"]["motivo"], "Dia de Nossa Senhora Auxiliadora", nome)
        self.assertNotIn("CALDAS NOVAS", self.cal["locais"])

    def test_motivo_de_descricao_quebrada_em_linhas(self) -> None:
        self.assertEqual(self.geral["2026-07-26"][0]["motivo"], "Fundação da Cidade de Goiás")
        self.assertEqual(self.geral["2026-10-12"][0]["motivo"],
                         "Dia de Nossa Senhora Aparecida (Padroeira do Brasil)")

    def test_natal_no_mesmo_dia_do_recesso(self) -> None:
        # 25/12 tem dois registros (recesso + feriado): conferir o conjunto, não o dicionário.
        tipos = {d["tipo"] for d in self.geral["2026-12-25"]}
        self.assertEqual(tipos, {"recesso", "sem_expediente"})

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjgo.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjgo.interpretar(tjgo.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjgo.FONTES[2026]])
        self.assertEqual(len(cal["geral"]), 32)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

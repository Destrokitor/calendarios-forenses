"""Testes do motor do TJPR. Só usam a FIXTURE (tests/fixtures/tjpr), nunca a rede.

A fixture é o Decreto Judiciário n.º 621/2025 - P-SEP (SEI 0064955-90.2025.8.16.6000), 7 páginas.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjpr
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjpr")
ARQUIVO = "decreto-judiciario-621-2025.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjpr.DECRETOS[2026]:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJPR(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjpr.MOTOR
        cls.cal = tjpr.interpretar(tjpr.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJPR", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        # Ficha, âncoras 1 a 4 (todas no Art. 1º ou Art. 2º, em geral).
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertEqual(self.geral["2026-02-17"]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-06-04"]["motivo"], "Corpus Christi")
        self.assertIn("Dia da Justiça", self.geral["2026-12-18"]["motivo"])
        self.assertEqual(self.geral["2026-02-16"]["motivo"], "Véspera de Carnaval")

    def test_ancora_local_sao_jose_dos_pinhais(self) -> None:
        # Ficha, âncora 5: 19/03 é do município, não do tribunal.
        self.assertNotIn("2026-03-19", self.geral)
        dias = {d["data"]: d for d in self.cal["locais"]["SÃO JOSÉ DOS PINHAIS"]}
        self.assertEqual(dias["2026-03-19"]["motivo"], "Dia do Padroeiro do Município")
        self.assertEqual(dias["2026-03-19"]["tipo"], "sem_expediente")
        # Art. 4º, 08/01: Emancipação Política, no mesmo município.
        self.assertIn("2026-01-08", dias)

    def test_curitiba_so_no_municipio(self) -> None:
        # Art. 1º: 08/09 é Padroeira de Curitiba, "somente no Município de Curitiba".
        self.assertNotIn("2026-09-08", self.geral)
        self.assertEqual(
            self.cal["locais"]["CURITIBA"],
            [{"data": "2026-09-08", "tipo": "sem_expediente", "motivo": "Padroeira de Curitiba", "fonte": tjpr.FONTE_ID}],
        )

    def test_suspensoes_sem_motivo_e_natal(self) -> None:
        # Art. 2º: 20/04 e 05/06 vêm sem motivo no decreto: o motor registra isso, sem inventar.
        self.assertEqual(self.geral["2026-04-20"]["motivo"], "Suspensão do expediente (sem motivo no decreto)")
        self.assertEqual(self.geral["2026-06-05"]["motivo"], "Suspensão do expediente (sem motivo no decreto)")
        # Art. 3º: 24 e 31/12 suspensos, sem compensação.
        self.assertEqual(self.geral["2026-12-24"]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-12-31"]["tipo"], "sem_expediente")

    def test_sem_recesso_e_sem_tipo_inventado(self) -> None:
        # O decreto não traz o recesso (20/12 a 06/01): nada de tipo recesso.
        self.assertFalse(self.motor.esperado["exige_recesso"])
        self.assertEqual([d for d in self.cal["geral"] if d["tipo"] == "recesso"], [])
        self.assertTrue(all(d["tipo"] == "sem_expediente" for d in todos_os_dias(self.cal)))

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 20)  # 14 do Art. 1º + 4 do Art. 2º + 2 do Art. 3º
        self.assertEqual(len(self.cal["locais"]), 162)  # 161 municípios do Art. 4º + Curitiba
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 348)

    def test_municipio_com_dois_dias_e_alias(self) -> None:
        # Piraquara: 29/01 (emancipação) e 06/08 (padroeiro).
        self.assertEqual([d["data"] for d in self.cal["locais"]["PIRAQUARA"]], ["2026-01-29", "2026-08-06"])
        # O decreto grafa "Bocaíuva" e "Bocaiúva": a chave é a forma oficial, uma só.
        self.assertIn("BOCAIÚVA DO SUL", self.cal["locais"])
        self.assertNotIn("BOCAÍUVA DO SUL", self.cal["locais"])
        self.assertEqual(
            [d["data"] for d in self.cal["locais"]["BOCAIÚVA DO SUL"]],
            ["2026-04-12", "2026-06-13", "2026-08-06"],
        )

    def test_dia_com_varios_municipios_e_motivo_limpo(self) -> None:
        # Art. 4º, 20/01: Sengés (Dia do Padroeiro do Município).
        dias = {d["data"]: d for d in self.cal["locais"]["SENGÉS"]}
        self.assertEqual(dias["2026-01-20"]["motivo"], "Dia do Padroeiro do Município")
        # Art. 4º, 08/12: "Sengés ( Dia de Imaculada Conceição)" tem espaço depois do parêntese.
        self.assertEqual(dias["2026-12-08"]["motivo"], "Dia de Imaculada Conceição")

    def test_item_sem_fechamento_de_parentese(self) -> None:
        # Art. 4º, 04/10: "Umuarama (Dia do Padroeiro do Município;" sem ")" no PDF.
        dias = {d["data"]: d for d in self.cal["locais"]["UMUARAMA"]}
        self.assertEqual(dias["2026-10-04"]["motivo"], "Dia do Padroeiro do Município")

    def test_todo_dia_tem_fonte_valida(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjpr.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjpr.interpretar(tjpr.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjpr.DECRETOS[2026]])
        self.assertEqual(len(cal["geral"]), 20)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

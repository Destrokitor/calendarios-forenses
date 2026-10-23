"""Testes do motor do TJTO. Só usam a FIXTURE (tests/fixtures/tjto), nunca a rede.

A fixture são as páginas 39 e 40 do Diário da Justiça nº 5995 (10/11/2025), com a Portaria nº 3741
(calendário de feriados e pontos facultativos de 2026).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjto
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjto")
ARQUIVO = "portaria-3741-2025-dj-5995-2025-11-10-pags39-40.pdf"

PONTOS_FACULTATIVOS = ["2026-04-20", "2026-06-05", "2026-08-10"]


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjto.FONTE_URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJTO(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjto.MOTOR
        cls.cal = tjto.interpretar(tjto.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}
        cls.palmas = {d["data"]: d for d in cls.cal["locais"]["PALMAS"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJTO", 2026, self.motor.esperado), [])

    def test_ancoras(self) -> None:
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertIn("carnaval", self.geral["2026-02-16"]["motivo"].lower())
        self.assertIn("carnaval", self.geral["2026-02-17"]["motivo"].lower())
        self.assertIn("semana santa", self.geral["2026-04-01"]["motivo"].lower())
        self.assertIn("semana santa", self.geral["2026-04-03"]["motivo"].lower())
        self.assertIn("servidor", self.geral["2026-10-30"]["motivo"].lower())
        self.assertIn("justiça", self.geral["2026-12-18"]["motivo"].lower())

    def test_contagem_e_tipos(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 19)
        self.assertTrue(all(d["tipo"] == "sem_expediente" for d in self.cal["geral"]))
        self.assertEqual(list(self.cal["locais"].keys()), ["PALMAS"])

    def test_sem_recesso(self) -> None:
        # A portaria não traz recesso; não inventar.
        self.assertFalse(any(d["tipo"] == "recesso" for d in todos_os_dias(self.cal)))

    def test_pontos_facultativos_ficam_fora(self) -> None:
        # Art. 3º: a portaria não diz se suspendem prazo; sem decisão, não entram como dia.
        for data in PONTOS_FACULTATIVOS:
            self.assertNotIn(data, self.geral)
            self.assertNotIn(data, self.palmas)

    def test_datas_transferidas_nao_geram_dia_original(self) -> None:
        # Art. 2º: 28/10 vira 30/10; 08/12 vira 18/12.
        self.assertNotIn("2026-10-28", self.geral)
        self.assertNotIn("2026-12-08", self.geral)

    def test_intervalos_em_texto(self) -> None:
        # "1º, 2 e 3 de abril" e "16 e 17 de fevereiro".
        for data in ("2026-04-01", "2026-04-02", "2026-04-03", "2026-02-16", "2026-02-17"):
            self.assertIn(data, self.geral)

    def test_capital_fica_no_local_nao_no_geral(self) -> None:
        # Art. 4º: 19/03 (Padroeiro de Palmas) e 20/05 (aniversário da cidade) só em Palmas.
        self.assertEqual(sorted(self.palmas), ["2026-03-19", "2026-05-20"])
        self.assertEqual(self.palmas["2026-03-19"]["tipo"], "sem_expediente")
        self.assertIn("Palmas", self.palmas["2026-03-19"]["motivo"])
        self.assertNotIn("2026-03-19", self.geral)
        self.assertNotIn("2026-05-20", self.geral)

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjto.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjto.interpretar(tjto.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjto.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 19)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

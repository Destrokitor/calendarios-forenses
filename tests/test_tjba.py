"""Testes do motor do TJBA. Só usam a FIXTURE (tests/fixtures/tjba), nunca a rede."""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.motores import tjba
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

ARQUIVO = os.path.join(os.path.dirname(__file__), "fixtures", "tjba", "decreto_1050_2025_expediente_forense_2026.pdf")


def _pdf() -> bytes:
    with open(ARQUIVO, "rb") as f:
        return f.read()


class RedeFalsa:
    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        return _pdf()


class TestTJBA(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjba.MOTOR
        cls.texto = tjba.pdf_para_texto(_pdf())
        cls.cal = tjba.interpretar(cls.texto, 2026)

    def tipos(self, data):
        return sorted(d["tipo"] for d in self.cal["geral"] if d["data"] == data)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJBA", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        for data in ("2026-02-12", "2026-02-13", "2026-02-16", "2026-02-17", "2026-02-18",
                     "2026-04-02", "2026-04-03", "2026-06-22", "2026-06-23", "2026-06-24",
                     "2026-07-02", "2026-07-03", "2026-12-07", "2026-12-08"):
            self.assertEqual(self.tipos(data), ["sem_expediente"], data)
        d = [x for x in self.cal["geral"] if x["data"] == "2026-02-18"][0]
        self.assertIn("Cinzas", d["motivo"])

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 6 + 14 + 28)
        self.assertEqual(list(self.cal["locais"]), ["SALVADOR"])

    def test_recesso_so_do_ano_pedido(self) -> None:
        rec = [d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso"]
        self.assertEqual(rec, ["2026-01-0%d" % n for n in range(1, 7)])

    def test_dia_com_dois_registros(self) -> None:
        self.assertEqual(self.tipos("2026-01-01"), ["recesso", "sem_expediente"])
        self.assertEqual(self.tipos("2026-01-02"), ["recesso", "sem_expediente"])
        self.assertEqual(self.tipos("2026-01-03"), ["recesso"])

    def test_suspensao_de_prazo_7_a_20_janeiro(self) -> None:
        for n in range(7, 21):
            self.assertEqual(self.tipos("2026-01-%02d" % n), ["suspensao_prazo"], n)
        self.assertEqual(self.tipos("2026-01-21"), [])

    def test_dia_do_servidor_transferido(self) -> None:
        self.assertEqual(self.tipos("2026-10-30"), ["sem_expediente"])
        self.assertEqual(self.tipos("2026-10-28"), [])

    def test_parcial_declara_municipais(self) -> None:
        self.assertIn("municipais", self.motor.parcial)

    def test_outro_ano(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjba.interpretar(self.texto, 2027)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())

    def test_coletar_com_rede_falsa(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjba.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 48)


if __name__ == "__main__":
    unittest.main()

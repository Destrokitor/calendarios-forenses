"""Testes do motor do TRT12. Só usam a FIXTURE (tests/fixtures/trt12), nunca a rede.

A fixture é a Portaria SEAP nº 191/2024 (republicação de 19/05/2025, alterada pela Portaria SEAP
nº 57/2025), que divulga os feriados do exercício de 2026. Ver docs/fichas/TRT12.md.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import trt12
from robo.motores.base import AindaNaoPublicado

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trt12")
PDF = os.path.join(FIX, "portaria_calendario_feriados_2026.pdf")
TXT = os.path.join(FIX, "portaria_calendario_feriados_2026.txt")


def _ler(caminho: str) -> bytes:
    with open(caminho, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != trt12.URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler(PDF)


class TestTRT12(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt12.MOTOR
        with open(TXT, encoding="utf-8") as f:
            cls.texto = f.read()
        cls.cal = trt12.interpretar(cls.texto, 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT12", 2026, self.motor.esperado), [])

    def test_contagens_minimas(self) -> None:
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertGreaterEqual(len(self.cal["locais"]), self.motor.esperado["min_locais"])
        self.assertEqual(len(self.cal["geral"]), 42)
        self.assertEqual(len(self.cal["locais"]), 31)

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        self.assertEqual(self.geral["2026-02-16"][0]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-08-10"][0]["tipo"], "sem_expediente")
        self.assertIn("transferido de 11/08", self.geral["2026-08-10"][0]["motivo"])
        self.assertIn("Data Magna", self.geral["2026-08-16"][0]["motivo"])

    def test_ancora_municipal_joinville(self) -> None:
        self.assertEqual(
            self.cal["locais"]["JOINVILLE"],
            [{"data": "2026-03-19", "tipo": "sem_expediente",
              "motivo": "Fundação da Cidade de Joinville", "fonte": "portaria"}])

    def test_recesso_janeiro_e_dezembro(self) -> None:
        for dia_n in range(1, 7):
            self.assertIn("recesso", [d["tipo"] for d in self.geral["2026-01-%02d" % dia_n]])
        for dia_n in range(20, 32):
            self.assertIn("recesso", [d["tipo"] for d in self.geral["2026-12-%02d" % dia_n]])

    def test_mesma_data_com_dois_registros(self) -> None:
        # 25/12 é Natal e também recesso; a data não pode ser guardada por dicionário único.
        tipos = sorted(d["tipo"] for d in self.geral["2026-12-25"])
        self.assertEqual(tipos, ["recesso", "sem_expediente"])
        self.assertEqual(len(self.geral["2026-11-02"]), 2)

    def test_transferidos_pelo_art_2(self) -> None:
        self.assertIn("2026-08-10", self.geral)
        self.assertNotIn("2026-08-11", self.geral)
        self.assertIn("2026-10-30", self.geral)
        self.assertNotIn("2026-10-28", self.geral)
        self.assertIn("2026-12-07", self.geral)
        self.assertNotIn("2026-12-08", self.geral)

    def test_semana_santa_e_carnaval(self) -> None:
        for dia_n in (16, 17, 18):
            self.assertIn("2026-02-%02d" % dia_n, self.geral)
        for dia_n in range(1, 6):
            self.assertIn("2026-04-%02d" % dia_n, self.geral)

    def test_local_com_quebra_de_linha(self) -> None:
        # Xanxerê: 27/02 e 06/03 têm o motivo quebrado em duas linhas no PDF; o motivo tem de vir inteiro.
        xanx = {d["data"]: d["motivo"] for d in self.cal["locais"]["XANXERÊ"]}
        self.assertEqual(xanx["2026-02-27"], "Fundação da Cidade de Xanxerê (alterada pela Portaria SEAP n. 57, de 16 de maio de 2025)")
        self.assertEqual(xanx["2026-03-06"], "Fundação da Cidade de Xanxerê (alterada pela Portaria SEAP n. 57, de 16 de maio de 2025)")
        self.assertNotIn("2026-03-09", xanx)

    def test_municipio_em_lista_e_multiplos(self) -> None:
        self.assertIn("2026-12-08", [d["data"] for d in self.cal["locais"]["CURITIBANOS"]])
        self.assertIn("2026-12-08", [d["data"] for d in self.cal["locais"]["FRAIBURGO"]])
        self.assertIn("2026-08-25", [d["data"] for d in self.cal["locais"]["JOAÇABA"]])
        self.assertIn("2026-08-25", [d["data"] for d in self.cal["locais"]["CHAPECÓ"]])

    def test_municipio_sem_data_na_fonte_fica_vazio(self) -> None:
        # DUVIDA do motor: Caçador aparece sem dia na extração; o local existe, sem dias.
        self.assertIn("CAÇADOR", self.cal["locais"])
        self.assertEqual(self.cal["locais"]["CAÇADOR"], [])

    def test_fora_do_ato_nao_inventa(self) -> None:
        # Suspensões de 2026 posteriores ao ato (ex.: SEAP 25/2026) e os dias 07/01 a 20/01 não entram.
        for data in ("2026-04-20", "2026-06-05", "2026-01-07", "2026-01-20", "2026-03-09"):
            self.assertNotIn(data, self.geral)
        for dias in self.cal["locais"].values():
            self.assertNotIn("2026-03-09", [d["data"] for d in dias])

    def test_tipos_parciais_e_suspensao_vazios(self) -> None:
        tipos = {d["tipo"] for d in todos_os_dias(self.cal)}
        self.assertNotIn("parcial", tipos)
        self.assertNotIn("suspensao_prazo", tipos)

    def test_ano_que_o_ato_nao_cobre(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt12.interpretar(self.texto, 2027)

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext não instalado")
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt12.URL])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], self.cal["locais"])

    def test_texto_do_pdf_bate_com_a_fixture_txt(self) -> None:
        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext não instalado")
        self.assertEqual(trt12.pdf_para_texto(_ler(PDF)), self.texto)


if __name__ == "__main__":
    unittest.main()

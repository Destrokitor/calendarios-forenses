"""Testes do motor do TJSE. Só usam a FIXTURE (tests/fixtures/tjse), nunca a rede.

A fixture é o PDF "Calendário 2026" do próprio TJSE, baixado em 23/10/2026 (ver ficha).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.motores import tjse
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjse")
PDF = os.path.join(FIX, "calendario-tjse-2026.pdf")

# Pontos facultativos (coluna da direita do PDF): não podem virar dia sem expediente.
PONTOS_FACULTATIVOS = ["2026-02-16", "2026-02-18", "2026-03-16", "2026-04-02", "2026-04-20",
                       "2026-06-05", "2026-08-10", "2026-12-07"]


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == tjse.CALENDARIOS[2026]:
            with open(PDF, "rb") as f:
                return f.read()
        raise AssertionError("URL fora da fixture: %s" % url)


def _datas(dias):
    return {d["data"] for d in dias}


class TestTJSE(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        with open(PDF, "rb") as f:
            cls.pdf = f.read()
        cls.motor = tjse.MOTOR
        cls.cal = tjse.interpretar(tjse.coluna_feriados(cls.pdf), 2026)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJSE", 2026, self.motor.esperado), [])

    def test_ancoras(self) -> None:
        geral = {d["data"]: d for d in self.cal["geral"]}
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, geral, nome)
        self.assertEqual(geral["2026-02-17"]["tipo"], "sem_expediente")
        self.assertIn("Carnaval", geral["2026-02-17"]["motivo"])
        self.assertIn("Emancipação Política de Sergipe", geral["2026-07-08"]["motivo"])
        self.assertIn("Dia do Magistrado", geral["2026-08-11"]["motivo"])
        self.assertIn("Dia do Funcionário Público", geral["2026-10-30"]["motivo"])
        self.assertEqual(geral["2026-12-20"]["tipo"], "recesso")

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 28)  # 16 feriados + 12 de recesso
        self.assertEqual(len(self.cal["locais"]), 51)
        self.assertGreaterEqual(sum(len(v) for v in self.cal["locais"].values()), 116)

    def test_pontos_facultativos_ficam_de_fora(self) -> None:
        geral = _datas(self.cal["geral"])
        for data in PONTOS_FACULTATIVOS:
            self.assertNotIn(data, geral, data)
        self.assertIn("pontos facultativos", self.motor.parcial.lower())

    def test_coluna_da_direita_nao_entra_na_leitura(self) -> None:
        texto = tjse.coluna_feriados(self.pdf)
        self.assertNotIn("FACULTATIV", texto.upper())
        self.assertNotIn("Quarta-feira de Cinzas", texto)

    def test_vazamento_de_facultativo_e_recusado(self) -> None:
        texto = tjse.coluna_feriados(self.pdf) + "\n16/02 – Carnaval\nPONTOS FACULTATIVOS\n"
        with self.assertRaises(ErroDeFonte):
            tjse.interpretar(texto, 2026)

    def test_recesso_so_dentro_do_ano(self) -> None:
        recesso = [d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso"]
        self.assertEqual(recesso, ["2026-12-%02d" % n for n in range(20, 32)])
        self.assertTrue(all(d["data"].startswith("2026-") for d in self.cal["geral"]))
        self.assertTrue(all(d["fonte"] == "calendario" for d in self.cal["geral"]))

    def test_local_aracaju(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["ARACAJU"]}
        self.assertIn("2026-03-17", dias)
        self.assertEqual(dias["2026-03-17"]["tipo"], "sem_expediente")
        self.assertIn("Aniversário da Capital", dias["2026-03-17"]["motivo"])
        self.assertEqual(dias["2026-03-17"]["fonte"], "calendario")
        # feriado municipal no mesmo dia do geral continua no local (decisão documentada no motor)
        self.assertIn("2026-12-08", dias)

    def test_motivo_quebrado_em_duas_linhas(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["TOBIAS BARRETO"]}
        self.assertEqual(dias["2026-06-07"]["motivo"],
                         "Aniversário de Nascimento de Tobias Barreto de Menezes")

    def test_nomes_de_municipio_normalizados(self) -> None:
        for chave in ("ITAPORANGA D'AJUDA", "N. SRA. DA GLÓRIA", "SÃO CRISTÓVÃO", "CRISTINÁPOLIS"):
            self.assertIn(chave, self.cal["locais"])
        self.assertTrue(all(k == k.upper() for k in self.cal["locais"]))

    def test_fontes_e_dias_validos(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        self.assertEqual(ids, {"calendario"})
        todos = [*self.cal["geral"], *[x for v in self.cal["locais"].values() for x in v]]
        for d in todos:
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])

    def test_ano_de_outro_pdf_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjse.interpretar(tjse.coluna_feriados(self.pdf), 2027)

    def test_ano_seguinte_ainda_nao_publicado(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])  # nem chegou a pedir o PDF

    def test_coletar_so_baixa_o_pdf_e_valida(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjse.CALENDARIOS[2026]])
        self.assertEqual(validacao.validar(cal, "TJSE", 2026, self.motor.esperado), [])

    def test_horario_nao_se_aplica(self) -> None:
        self.assertFalse(any("horario" in d for d in self.cal["geral"]))


if __name__ == "__main__":
    unittest.main()

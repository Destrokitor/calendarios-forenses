"""Testes do motor do TJAC. Só usam a FIXTURE (tests/fixtures/tjac), nunca a rede.

A fixture é a Portaria PRESI nº 6569/2025 (DJe 7.950, 3.2.2026), com o calendário de 2026.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjac
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjac")
ARQUIVO = "portaria_presi_6569_2025.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjac.EDICOES[2026]:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJAC(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjac.MOTOR
        cls.cal = tjac.interpretar(tjac.pdf_para_palavras(_ler_pdf()), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def _dias_do_local(self, nome: str):
        return {d["data"]: d for d in self.cal["locais"][nome]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJAC", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        # Ficha, itens 1 a 3: feriado nacional, carnaval e quarta de cinzas (feriado forense), e
        # aniversário do Estado do Acre.
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertIn("Confraternização", self.geral["2026-01-01"]["motivo"])
        for n in (16, 17, 18):
            self.assertEqual(self.geral["2026-02-%02d" % n]["tipo"], "sem_expediente")
        self.assertIn("Cinzas", self.geral["2026-02-18"]["motivo"])
        self.assertEqual(self.geral["2026-06-15"]["motivo"], "Aniversário do Estado do Acre")

    def test_contagem_geral(self) -> None:
        # 9 nacionais, 6 estaduais, 3 de carnaval (forense) e 2 regimentais. Fora: as 3 adiadas
        # (20/01, 28/10, 17/11) e os pontos facultativos.
        self.assertEqual(len(self.cal["geral"]), 20)
        self.assertTrue(all(d["tipo"] == "sem_expediente" for d in self.cal["geral"]))

    def test_municipal_fica_no_local_e_nao_no_geral(self) -> None:
        # Ficha, item 4: aniversário de Marechal Thaumaturgo é da comarca, não do tribunal.
        self.assertNotIn("2026-11-05", self.geral)
        dias = self._dias_do_local("MARECHAL THAUMATURGO")
        self.assertEqual(dias["2026-11-05"]["tipo"], "sem_expediente")
        self.assertEqual(dias["2026-11-05"]["motivo"], "Aniversário do Município de Marechal Thaumaturgo")

    def test_rio_branco_capital(self) -> None:
        # Ficha, item 5: aniversário de Rio Branco, feriado municipal da capital.
        dias = self._dias_do_local("RIO BRANCO")
        self.assertEqual(dias["2026-12-28"]["motivo"], "Aniversário do Município de Rio Branco")
        self.assertNotIn("2026-12-28", self.geral)

    def test_municipio_sem_nome_no_evento(self) -> None:
        # Na tabela, "Municipal" sem parênteses: o nome vem do próprio evento.
        self.assertIn("2026-06-25", self._dias_do_local("PORTO WALTER"))

    def test_linha_com_varios_municipios(self) -> None:
        # Linha de 14/05: Senador Guiomard, Assis Brasil e Manoel Urbano.
        for nome in ("SENADOR GUIOMARD", "ASSIS BRASIL", "MANOEL URBANO"):
            self.assertIn("2026-05-14", self._dias_do_local(nome), nome)

    def test_celula_quebrada_em_varias_linhas(self) -> None:
        # Linha de 28/04: oito municípios, em célula que ocupa cinco linhas do PDF.
        nomes = ("ACRELÂNDIA", "BUJARI", "CAPIXABA", "EPITACIOLÂNDIA", "JORDÃO", "MARECHAL THAUMATURGO",
                 "SANTA ROSA DO PURUS", "PORTO ACRE")
        for nome in nomes:
            self.assertIn("2026-04-28", self._dias_do_local(nome), nome)
        self.assertNotIn("2026-04-28", self.geral)
        self.assertNotIn("SANTA ROSA DO PURUS PORTO ACRE", self.cal["locais"])

    def test_nome_com_preposicao_preservado(self) -> None:
        # "(Plácido de Castro)" é um só município.
        self.assertIn("PLÁCIDO DE CASTRO", self.cal["locais"])
        self.assertIn("2026-03-30", self._dias_do_local("PLÁCIDO DE CASTRO"))

    def test_ponto_facultativo_fica_de_fora(self) -> None:
        # DUVIDA da ficha: pontos facultativos (estaduais e municipais) não entram em nenhuma lista.
        pontos = ["2026-06-04", "2026-08-06", "2026-12-24", "2026-12-31",  # estaduais
                  "2026-05-18", "2026-07-13", "2026-08-22", "2026-09-08", "2026-09-25",
                  "2026-10-31"]  # municipais
        todas = {d["data"] for d in todos_os_dias(self.cal)}
        for data in pontos:
            self.assertNotIn(data, todas, data)

    def test_datas_adiadas_ficam_de_fora(self) -> None:
        # DUVIDA da ficha: a data original não entra, e a data para onde foi transferida também não.
        for data in ("2026-01-20", "2026-10-28", "2026-11-17"):
            self.assertNotIn(data, self.geral, data)
        for data in ("2026-01-22", "2026-10-30", "2026-11-19"):
            self.assertNotIn(data, self.geral, data)
        # Mas o município da mesma data continua: São Sebastião (Xapuri e Epitaciolândia), 20/01.
        self.assertIn("2026-01-20", self._dias_do_local("XAPURI"))

    def test_sem_recesso(self) -> None:
        # O ato não traz recesso: nada de "recesso" e exige_recesso é False.
        self.assertFalse(any(d["tipo"] == "recesso" for d in self.cal["geral"]))
        self.assertFalse(self.motor.esperado["exige_recesso"])

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjac.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjac.EDICOES[2026]])
        self.assertEqual(len(cal["geral"]), 20)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjac.interpretar(tjac.pdf_para_palavras(_ler_pdf()), 2027)


if __name__ == "__main__":
    unittest.main()

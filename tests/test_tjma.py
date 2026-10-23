"""Testes do motor do TJMA. Só usam a FIXTURE (tests/fixtures/tjma), nunca a rede.

A fixture é a Resolução-GP nº 131/2025 (calendário de 2026), em PDF com camada de texto.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjma
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjma")
ARQUIVO = "resolucao_gp_131_2025.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjma.FONTE_URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJMA(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjma.MOTOR
        cls.cal = tjma.interpretar(tjma.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}
        cls.sao_luis = cls.cal["locais"][tjma.normalizar_local(tjma.LOCAL_SAO_LUIS)]

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJMA", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertEqual(self.geral["2026-01-01"]["motivo"], "Dia da Confraternização Universal")
        self.assertEqual(self.geral["2026-07-28"]["tipo"], "sem_expediente")
        self.assertIn("dia do advogado", self.geral["2026-08-11"]["motivo"].lower())

    def test_contagem_geral(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 17)  # incisos I a XVII
        self.assertEqual(len({d["data"] for d in self.cal["geral"]}), 17)  # uma data por inciso

    def test_carnaval_sao_dois_dias(self) -> None:
        for data in ("2026-02-16", "2026-02-17"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente")
            self.assertIn("Carnaval", self.geral[data]["motivo"])
        # A citação da lei (§ 1º do art. 5º-A da LC 14/1991) sai do motivo.
        self.assertNotIn("(§", self.geral["2026-02-16"]["motivo"])

    def test_corpus_christi_e_inciso_viii(self) -> None:
        self.assertEqual(self.geral["2026-06-04"]["tipo"], "sem_expediente")
        self.assertIn("Corpus Christi", self.geral["2026-06-04"]["motivo"])

    def test_locais_so_sao_luis(self) -> None:
        self.assertEqual(list(self.cal["locais"].keys()), ["SÃO LUÍS"])
        self.assertEqual(len(self.sao_luis), 2)

    def test_feriados_municipais_de_sao_luis(self) -> None:
        dias = {d["data"]: d for d in self.sao_luis}
        self.assertEqual(set(dias), {"2026-06-29", "2026-09-08"})
        self.assertIn("São Pedro", dias["2026-06-29"]["motivo"])
        self.assertIn("Fundação da Cidade", dias["2026-09-08"]["motivo"])
        self.assertEqual(dias["2026-06-29"]["tipo"], "sem_expediente")
        # São Pedro e a Fundação não valem para o estado: não podem estar em geral.
        self.assertNotIn("2026-06-29", self.geral)
        self.assertNotIn("2026-09-08", self.geral)

    def test_pontos_facultativos_ficam_de_fora(self) -> None:
        # Art. 3º (18/02, 01/04, 05/06): o ato não diz se suspendem prazo; não podem virar sem_expediente.
        for data in ("2026-02-18", "2026-04-01", "2026-06-05"):
            self.assertNotIn(data, self.geral)
            self.assertNotIn(data, {d["data"] for d in self.sao_luis})

    def test_sem_recesso_e_tipos_validos(self) -> None:
        self.assertFalse(any(d["tipo"] == "recesso" for d in self.cal["geral"]))
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjma.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_parcial_declara_a_lacuna_da_res_26(self) -> None:
        self.assertIn("26", self.motor.parcial)
        self.assertIn("07/04/2026", self.motor.parcial)

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjma.interpretar(tjma.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjma.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 17)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

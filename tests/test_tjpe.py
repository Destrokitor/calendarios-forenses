"""Testes do motor do TJPE. Só usam a FIXTURE (tests/fixtures/tjpe), nunca a rede.

A fixture é o Ato Conjunto nº 43/2025 (DJe 304/2025, de 14/10/2025), calendário de 2026.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjpe
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjpe")
ARQUIVO = "ato-conjunto-43-2025-dje-304.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjpe.FONTE_URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJPE(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjpe.MOTOR
        cls.cal = tjpe.interpretar(tjpe.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def tipos(self, data: str) -> set:
        return {d["tipo"] for d in self.geral.get(data, [])}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJPE", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        self.assertEqual(self.tipos("2026-06-22"), {"sem_expediente"})
        self.assertIn("Corpus Christi", self.geral["2026-06-22"][0]["motivo"])
        self.assertIn("Data Magna", self.geral["2026-03-06"][0]["motivo"])
        self.assertIn("Servidor", self.geral["2026-10-30"][0]["motivo"])
        self.assertEqual(self.tipos("2026-12-20"), {"recesso"})
        self.assertEqual(self.tipos("2026-12-31"), {"recesso"})

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 44)  # 21 feriados + 23 dias de recesso
        self.assertEqual(sum(1 for d in self.cal["geral"] if d["tipo"] == "sem_expediente"), 21)
        self.assertEqual(sum(1 for d in self.cal["geral"] if d["tipo"] == "recesso"), 23)

    def test_recesso_por_dias_soltos(self) -> None:
        recesso = sorted(d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso")
        esperado = (["2026-01-%02d" % n for n in range(2, 7)]
                    + ["2026-06-23"] + ["2026-06-%02d" % n for n in range(25, 31)]
                    + ["2026-12-%02d" % n for n in (20, 21, 22, 23, 24)]
                    + ["2026-12-%02d" % n for n in range(26, 32)])
        self.assertEqual(recesso, sorted(esperado))

    def test_natal_e_recesso_nao_se_repetem(self) -> None:
        # 25/12 é Natal (inciso XXI), não está no parágrafo único: uma só entrada, sem_expediente.
        self.assertEqual(self.tipos("2026-12-25"), {"sem_expediente"})
        self.assertIn("Natal", self.geral["2026-12-25"][0]["motivo"])
        # 24/06 é São João (inciso XII); 23/06 é recesso.
        self.assertEqual(self.tipos("2026-06-24"), {"sem_expediente"})
        self.assertEqual(self.tipos("2026-06-23"), {"recesso"})

    def test_carnaval_e_expediente_normal_de_13_02(self) -> None:
        for n in (16, 17, 18):
            self.assertEqual(self.tipos("2026-02-%02d" % n), {"sem_expediente"}, n)
        # Art. 3º: 13/02 tem expediente normal (trabalho remoto em alguns prédios). Não é dia sem expediente.
        self.assertNotIn("2026-02-13", self.geral)

    def test_domingos_listados_como_feriado(self) -> None:
        # 05/04 (Páscoa) e 15/11 (Proclamação) caem em domingo mas estão no ato.
        self.assertEqual(self.tipos("2026-04-05"), {"sem_expediente"})
        self.assertEqual(self.tipos("2026-11-15"), {"sem_expediente"})

    def test_antecipacao_e_transferencias(self) -> None:
        # 10/08 antecipado do dia 11/08 (inciso XIII): o 11/08 não é feriado.
        self.assertEqual(self.tipos("2026-08-10"), {"sem_expediente"})
        self.assertNotIn("2026-08-11", self.geral)
        # 04/06 (Corpus Christi original) não é feriado: foi transferido para 22/06.
        self.assertNotIn("2026-06-04", self.geral)

    def test_local_recife(self) -> None:
        self.assertEqual(list(self.cal["locais"].keys()), ["RECIFE"])
        dias = self.cal["locais"]["RECIFE"]
        self.assertEqual([d["data"] for d in dias], ["2026-07-16"])
        self.assertEqual(dias[0]["tipo"], "sem_expediente")
        self.assertIn("Nossa Senhora do Carmo", dias[0]["motivo"])
        # Feriado municipal do Recife não vira dia geral do tribunal.
        self.assertNotIn("2026-07-16", self.geral)

    def test_interior_fora_da_lista(self) -> None:
        # Art. 4º: interior depende de lei municipal, sem lista no ato. Nenhum outro local.
        self.assertEqual(len(self.cal["locais"]), 1)
        self.assertEqual(self.motor.esperado["min_locais"], 1)

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjpe.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjpe.interpretar(tjpe.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_sem_endereco(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjpe.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 44)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

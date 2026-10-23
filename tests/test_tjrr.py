"""Testes do motor do TJRR. Só usam a FIXTURE (tests/fixtures/tjrr), nunca a rede.

A fixture é a capa e as páginas 3 a 7 do DJe 8006 (22/12/2025), com a Portaria TJRR/PR n. 1558
e o Anexo Único (calendário de 2026).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import tjrr
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjrr")
ARQUIVO = "portaria-1558-2025-dje-8006-2025-12-22-pags1e3a7.pdf"


def _ler_pdf() -> bytes:
    with open(os.path.join(FIX, ARQUIVO), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url != tjrr.FONTE_URL:
            raise AssertionError("URL fora da fixture: %s" % url)
        return _ler_pdf()


class TestTJRR(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjrr.MOTOR
        cls.cal = tjrr.interpretar(tjrr.pdf_para_texto(_ler_pdf()), 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJRR", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        # Itens 1 a 3 da ficha: recesso de 01 a 06/01, carnaval e quarta de cinzas, recesso de 20 a 31/12.
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral)
        # Em 01 e 02/01 há mais de um registro na data (feriado ou ponto + recesso): conferir o conjunto.
        for n in range(1, 7):
            tipos = {d["tipo"] for d in self.cal["geral"] if d["data"] == "2026-01-%02d" % n}
            self.assertIn("recesso", tipos, n)
        tipos_1 = {d["tipo"] for d in self.cal["geral"] if d["data"] == "2026-01-01"}
        self.assertEqual(tipos_1, {"recesso", "sem_expediente"})
        self.assertEqual(self.geral["2026-01-06"]["motivo"], "Recesso forense")
        for n in (16, 17, 18):
            self.assertEqual(self.geral["2026-02-%02d" % n]["tipo"], "sem_expediente")
        self.assertIn("carnaval", self.geral["2026-02-16"]["motivo"].lower())
        self.assertIn("cinzas", self.geral["2026-02-18"]["motivo"].lower())
        for n in range(20, 32):
            tipos = {d["tipo"] for d in self.cal["geral"] if d["data"] == "2026-12-%02d" % n}
            self.assertIn("recesso", tipos, n)

    def test_recesso_e_so_recesso(self) -> None:
        recesso = [d["data"] for d in self.cal["geral"] if d["tipo"] == "recesso"]
        self.assertEqual(len(recesso), 18)  # 01 a 06/01 (6) e 20 a 31/12 (12)
        self.assertTrue(all(d.startswith(("2026-01", "2026-12")) for d in recesso))

    def test_ponto_facultativo_suspende_como_sem_expediente(self) -> None:
        # Art. 3º da portaria: ponto facultativo também suspende expediente e prazos.
        dia = self.geral["2026-12-24"]
        self.assertEqual(dia["tipo"], "sem_expediente")
        self.assertIn("Ponto Facultativo", dia["motivo"])

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 44)  # 18 recesso + 26 feriados e pontos
        self.assertEqual(len(self.cal["locais"]), 9)  # comarcas da ficha
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 32)

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        for d in todos_os_dias(self.cal):
            self.assertEqual(d["fonte"], tjrr.FONTE_ID)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_item_da_capital_fica_no_local_nao_no_geral(self) -> None:
        # Ficha, item 4: aniversário de Boa Vista é da comarca, não do tribunal.
        self.assertNotIn("2026-07-09", self.geral)
        dias = {d["data"]: d for d in self.cal["locais"]["BOA VISTA"]}
        self.assertEqual(dias["2026-07-09"]["tipo"], "sem_expediente")
        self.assertEqual(dias["2026-07-09"]["motivo"], "Aniversário do Município de Boa Vista")

    def test_local_do_interior(self) -> None:
        # Ficha, item 5: aniversário de Caracaraí, só na comarca de Caracaraí.
        dias = {d["data"]: d for d in self.cal["locais"]["CARACARAÍ"]}
        self.assertEqual(dias["2026-05-27"]["motivo"], "Aniversário do Município de Caracaraí")
        self.assertNotIn("2026-05-27", {d["data"] for d in self.cal["locais"]["BOA VISTA"]})

    def test_linha_com_varias_comarcas(self) -> None:
        # "Comarcas de Mucajaí, São Luiz do Anauá, Alto Alegre e Bonfim", em 01/07.
        for nome in ("MUCAJAÍ", "SÃO LUIZ DO ANAUÁ", "ALTO ALEGRE", "BONFIM"):
            self.assertIn("2026-07-01", {d["data"] for d in self.cal["locais"][nome]}, nome)

    def test_comarca_quebrada_em_duas_linhas(self) -> None:
        # "Comarca de Alto de / Alegre e Posto Avançado de Caroebe", em 15/05.
        for nome in ("ALTO ALEGRE", "POSTO AVANÇADO DE CAROEBE E DE IRACEMA"):
            self.assertIn("2026-05-15", {d["data"] for d in self.cal["locais"][nome]}, nome)

    def test_comarca_com_mais_de_um_nome_em_uma_linha(self) -> None:
        # "Comarca de Bonfim e / Caracaraí", em 19/01 e 20/01.
        for nome in ("BONFIM", "CARACARAÍ"):
            self.assertIn("2026-01-20", {d["data"] for d in self.cal["locais"][nome]}, nome)

    def test_local_sem_dia_proprio_fica_na_lista(self) -> None:
        # Rorainópolis só tem o dia de Pacaraima e Rorainópolis; comarcas são sempre chaves.
        self.assertIn("RORAINÓPOLIS", self.cal["locais"])
        self.assertEqual([d["data"] for d in self.cal["locais"]["RORAINÓPOLIS"]], ["2026-10-17"])

    def test_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjrr.interpretar(tjrr.pdf_para_texto(_ler_pdf()), 2027)

    def test_coletar_com_rede_falsa_e_ano_seguinte(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjrr.FONTE_URL])
        self.assertEqual(len(cal["geral"]), 44)
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, RedeFalsa())


if __name__ == "__main__":
    unittest.main()

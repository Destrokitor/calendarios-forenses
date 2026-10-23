"""Testes do motor do TJMG. Só usam a FIXTURE (tests/fixtures/tjmg), nunca a rede.

A fixture é o PDF compilado da Portaria Conjunta 1.798/2026 (com as alterações 1.814, 1.828 e
1.860), baixado em 23/10/2026 (ver ficha). O texto é o `pdftotext -layout` guardado ao lado.
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.motores import tjmg
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjmg")
PDF = os.path.join(FIX, "pc1798_2026.pdf")
TXT = os.path.join(FIX, "pc1798_2026.txt")


class RedeFalsa:
    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == tjmg.PORTARIAS[2026]:
            with open(PDF, "rb") as f:
                return f.read()
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTJMG(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(TXT, encoding="utf-8") as f:
            cls.texto = f.read()
        cls.motor = tjmg.MOTOR
        cls.cal = tjmg.interpretar(cls.texto, 2026)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJMG", 2026, self.motor.esperado), [])

    def test_ancoras_gerais(self) -> None:
        geral = [(d["data"], d["tipo"], d["motivo"]) for d in self.cal["geral"]]
        for data in ("2026-02-16", "2026-02-17", "2026-02-18"):
            self.assertIn((data, "sem_expediente", "Segunda e Terça-feira de Carnaval e Quarta-feira de Cinzas"), geral)
        self.assertTrue(any(d == "2026-10-30" and "Funcionário Público" in m for d, _, m in geral))
        recesso = sorted(d for d, t, _ in geral if t == "recesso" and d >= "2026-12-01")
        self.assertEqual(recesso, ["2026-12-%02d" % n for n in range(20, 32)])

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 51)
        self.assertEqual(len(self.cal["locais"]), 298)  # 297 comarcas do Anexo + Belo Horizonte
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 1571)

    def test_data_com_dois_registros(self) -> None:
        # 1º/01 é feriado e também Feriado Forense (recesso); 25/12 idem
        for data in ("2026-01-01", "2026-12-25"):
            tipos = sorted(d["tipo"] for d in self.cal["geral"] if d["data"] == data)
            self.assertEqual(tipos, ["recesso", "sem_expediente"], data)

    def test_belo_horizonte(self) -> None:
        bh = {d["data"]: d for d in self.cal["locais"]["BELO HORIZONTE"]}
        self.assertEqual(sorted(bh), ["2026-06-04", "2026-06-05", "2026-08-15"])
        self.assertEqual(bh["2026-06-04"]["motivo"], "Corpus Christi")  # âncora 4 da ficha
        self.assertIn("art. 2º", bh["2026-06-05"]["motivo"])

    def test_comarca_do_anexo_abaete(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["ABAETÉ"]}
        self.assertEqual(dias["2026-06-13"]["motivo"], "Santo Antônio das Tabocas")  # âncora 5
        self.assertEqual(dias["2026-11-05"]["motivo"], "Aniversário da Cidade")
        self.assertEqual(dias["2026-06-13"]["fonte"], "portaria")

    def test_nome_de_comarca_quebrado_em_duas_linhas(self) -> None:
        for chave in ("VISCONDE DO RIO BRANCO", "SÃO ROQUE DE MINAS", "SÃO SEBASTIÃO DO PARAÍSO", "CARMO DO RIO CLARO"):
            self.assertIn(chave, self.cal["locais"])
        self.assertEqual(len(self.cal["locais"]["VISCONDE DO RIO BRANCO"]), 6)  # 5 itens + 5/6
        self.assertFalse([k for k in self.cal["locais"] if " - " in k])

    def test_item_quebrado_e_dias_multiplos(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["VAZANTE"]}
        self.assertIn("2026-05-02", dias)  # "2 e 3 de maio"
        self.assertIn("2026-05-03", dias)
        senador = {d["data"]: d["motivo"] for d in self.cal["locais"]["SENADOR FIRMINO"]}
        self.assertEqual(senador["2026-08-15"],
                         "Encerramento das comemorações do Jubileu de Nossa Senhora da Conceição")

    def test_so_o_primeiro_anexo(self) -> None:
        # os Anexos históricos repetem as comarcas; ler todos daria "comarca repetida"
        _, anexo = tjmg._parte_anexo(self.texto)
        self.assertEqual(len(tjmg.comarcas_do_anexo(anexo)), 297)
        self.assertLess(len(anexo.splitlines()), 1600)

    def test_ponte_de_corpus_christi(self) -> None:
        # 5/6 só onde 4/6 é feriado municipal (Corpus Christi)
        com = [k for k, v in self.cal["locais"].items()
               if any(d["data"] == "2026-06-05" for d in v)]
        com_corpus = [k for k, v in self.cal["locais"].items()
                      if any(d["data"] == "2026-06-04" and "Corpus" in d["motivo"] for d in v)]
        self.assertEqual(sorted(com), sorted(com_corpus))
        self.assertIn("ABAETÉ", com)
        self.assertFalse(any(d["data"] == "2026-06-05" for d in self.cal["geral"]))

    def test_suspensao_de_prazo_e_sem_expediente_avulso(self) -> None:
        susp = [d["data"] for d in self.cal["geral"] if d["tipo"] == "suspensao_prazo"]
        self.assertEqual(susp, ["2026-01-%02d" % n for n in range(7, 21)])
        avulsos = [d["data"] for d in self.cal["geral"] if "parágrafo único" in d["motivo"] and d["tipo"] == "sem_expediente"]
        self.assertEqual(sorted(avulsos), ["2026-04-20", "2026-12-07"])  # DUVIDA da ficha

    def test_horario_nao_se_aplica(self) -> None:
        self.assertFalse(any("horario" in d for d in self.cal["geral"]))

    def test_parcial_declara_o_que_fica_fora(self) -> None:
        self.assertIn("portaria local", self.motor.parcial)

    def test_ano_errado_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjmg.interpretar(self.texto, 2027)

    def test_anexo_ausente_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjmg.interpretar(self.texto.split("ANEXO ÚNICO")[0], 2026)

    def test_ano_seguinte_ainda_nao_publicado(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])

    def test_coletar_baixa_o_pdf(self) -> None:
        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext não instalado")
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjmg.PORTARIAS[2026]])
        self.assertEqual(validacao.validar(cal, "TJMG", 2026, self.motor.esperado), [])
        self.assertEqual(len(cal["locais"]), 298)


if __name__ == "__main__":
    unittest.main()

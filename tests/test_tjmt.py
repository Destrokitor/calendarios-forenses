"""Testes do motor do TJMT. Só usam as FIXTURES (tests/fixtures/tjmt), nunca a rede.

PDF = Portaria TJMT/PRES 1915/2025 (Anexos I e II); HTML = índice "Calendário Judiciário 2026"
(com a Portaria 1254/2026), ambos guardados em 23/10/2026 (ver docs/fichas/TJMT.md).
"""
from __future__ import annotations

import os
import shutil
import unittest

from robo import validacao
from robo.modelo import TIPOS
from robo.motores import tjmt
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjmt")
PDF = os.path.join(FIX, "portaria_1915_2025_pres_calendario_forense_2026.pdf")
HTML = os.path.join(FIX, "calendario_judiciario_2026_pagina.html")


def _ler(caminho: str) -> bytes:
    with open(caminho, "rb") as f:
        return f.read()


class RedeFalsa:
    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == tjmt.URL_PORTARIA[2026]:
            return _ler(PDF)
        if url == tjmt.URL_INDICE[2026]:
            return _ler(HTML)
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTJMT(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjmt.MOTOR
        cls.texto = tjmt.pdf_para_texto(_ler(PDF))
        cls.indice = _ler(HTML)
        cls.cal = tjmt.interpretar((cls.texto, cls.indice), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJMT", 2026, self.motor.esperado), [])

    def test_contagens(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 24)
        self.assertEqual(len(self.cal["locais"]), 79)
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 184)  # 184 datas contadas à parte no texto
        self.assertEqual(set(self.cal["locais"]) & {""}, set())

    def test_ancoras_do_anexo_i(self) -> None:
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, self.geral, data)
        self.assertIn("Tiradentes", self.geral["2026-04-20"][0]["motivo"])
        self.assertIn("ponto facultativo", self.geral["2026-04-20"][0]["motivo"])
        self.assertIn("feriado nacional", self.geral["2026-04-21"][0]["motivo"])
        for data in ("2026-12-07", "2026-12-08"):
            self.assertIn("Dia da Justiça", self.geral[data][0]["motivo"])
        self.assertEqual(self.geral["2026-01-01"][0]["tipo"], "sem_expediente")

    def test_cinzas_e_dia_parcial(self) -> None:
        d = self.geral["2026-02-18"][0]
        self.assertEqual(d["tipo"], "parcial")
        self.assertIn("13h", d["horario"])
        self.assertTrue(d["motivo"].count("(") == d["motivo"].count(")"))
        self.assertEqual([x["data"] for x in self.cal["geral"] if x["tipo"] == "parcial"], ["2026-02-18"])

    def test_ponto_facultativo_suspende_expediente_e_nao_vira_prazo(self) -> None:
        for data in ("2026-02-16", "2026-02-17", "2026-04-02", "2026-06-04", "2026-12-24", "2026-12-31"):
            self.assertEqual(self.geral[data][0]["tipo"], "sem_expediente", data)
        self.assertFalse(any(d["tipo"] in ("suspensao_prazo", "recesso") for d in self.cal["geral"]))

    def test_mes_herdado_nos_blocos_sem_rotulo(self) -> None:
        # 04/06 vem antes do rótulo JUNHO; 24/12 e 25/12 não têm rótulo
        for data in ("2026-06-04", "2026-12-24", "2026-12-25", "2026-12-31", "2026-04-02", "2026-08-10"):
            self.assertIn(data, self.geral)

    def test_dia_do_servidor_portaria_1254(self) -> None:
        self.assertNotIn("2026-10-28", self.geral)
        d = self.geral["2026-10-30"][0]
        self.assertIn("Dia do Servidor", d["motivo"])
        self.assertIn("1254/2026", d["motivo"])
        self.assertEqual(d["tipo"], "sem_expediente")
        self.assertEqual(d["fonte"], "indice")

    def test_sem_o_indice_o_dia_do_servidor_fica_em_28_10(self) -> None:
        cal = tjmt.interpretar((self.texto, "<html></html>"), 2026)
        self.assertIn("2026-10-28", {d["data"] for d in cal["geral"]})

    def test_alteracao_que_nao_casa_e_erro(self) -> None:
        html = ("<p>Altera o Anexo I: transferir o ponto facultativo do dia 27 de outubro de 2026 - X - "
                "para o dia 30 de outubro de 2026.</p>")
        with self.assertRaises(ErroDeFonte):
            tjmt.interpretar((self.texto, html), 2026)

    def test_ancoras_do_anexo_ii(self) -> None:
        agua = {d["data"]: d["motivo"] for d in self.cal["locais"]["ÁGUA BOA"]}
        self.assertEqual(agua, {"2026-07-09": "Aniversário do Município", "2026-10-12": "N. S. Aparecida (Padroeira)"})
        caceres = {d["data"]: d["motivo"] for d in self.cal["locais"]["CÁCERES"]}
        self.assertEqual(caceres, {"2026-08-25": "São Luiz de Cáceres (Padroeiro)", "2026-10-06": "Aniversário do Município"})

    def test_conferencia_a_mao_de_colunas_misturadas(self) -> None:
        loc = self.cal["locais"]

        def mot(nome, data):
            return [d["motivo"] for d in loc[nome] if d["data"] == data]
        # nome da comarca em duas linhas
        self.assertIn("CAMPO NOVO DO PARECIS", loc)
        self.assertIn("VILA BELA DA SANTÍSSIMA TRINDADE", loc)
        self.assertIn("MIRASSOL D'OESTE", loc)
        # motivo escorrido para a linha da data vizinha
        self.assertEqual(mot("GUIRATINGA", "2026-06-24"), ["São João Batista (Padroeiro)"])
        self.assertEqual(mot("GUIRATINGA", "2026-08-02"), ["Aniversário do Município"])
        self.assertEqual(mot("SÃO JOSÉ DOS QUATRO MARCOS", "2026-06-15"), ["Aniversário do Município"])
        self.assertEqual(mot("SÃO JOSÉ DOS QUATRO MARCOS", "2026-12-14"), ["Emancipação Política"])
        self.assertEqual(mot("SÃO JOSÉ DOS QUATRO MARCOS", "2026-05-12"),
                         ["Falecimento do Padre George Joseph Pierre Marie Martin"])
        # motivo em duas linhas, hífen no fim da linha, datas com ponto, erro de impressão
        self.assertEqual(mot("ARAPUTANGA", "2026-01-20"), ["Memorial em Homenagem ao Monsenhor Ermínio Celso Duca"])
        self.assertEqual(mot("CUIABÁ", "2026-04-08"), ["Aniversário de Cuiabá"])
        self.assertEqual(mot("SANTO ANTÔNIO DE LEVERGER", "2026-06-13"), ["Aniversário do Município"])
        self.assertEqual(mot("ARIPUANÃ", "2026-12-31"), ["Aniversário do Município"])
        self.assertEqual(mot("ARIPUANÃ", "2026-10-31"), ["Dia do Evangélico"])
        self.assertEqual(mot("NORTELÂNDIA", "2026-02-05"), ["Aniversário do Município"])
        # bloco com linha em branco no meio (Juína) e número na linha da data (Cáceres, Nova Mutum)
        self.assertEqual([d["data"] for d in loc["JUÍNA"]], ["2026-05-05", "2026-06-12", "2026-10-31"])
        self.assertEqual([d["data"] for d in loc["NOVA MUTUM"]], ["2026-07-04"])
        self.assertEqual(len(loc["PONTES E LACERDA"]), 1)
        self.assertEqual(len(loc["BRASNORTE"]), 1)

    def test_vila_bela_21_07_e_ponto_facultativo_local(self) -> None:
        vb = {d["data"]: d for d in self.cal["locais"]["VILA BELA DA SANTÍSSIMA TRINDADE"]}
        self.assertEqual(vb["2026-03-20"]["motivo"], "Ponto facultativo")
        self.assertIn("Dança do Congo", vb["2026-07-20"]["motivo"])
        self.assertIn("12h", vb["2026-07-21"]["motivo"])
        self.assertEqual(vb["2026-07-21"]["tipo"], "sem_expediente")

    def test_feriado_em_fim_de_semana_consta(self) -> None:
        self.assertIn("2026-05-24", {d["data"] for d in self.cal["locais"]["ALTO ARAGUAIA"]})
        self.assertIn("2026-11-15", self.geral)

    def test_data_com_dia_da_semana_errado_no_pdf_fica_como_escrita(self) -> None:
        # Nova Xavantina: "14/04 (domingo)"; 14/04/2026 é terça. A data (não o nome do dia) vale.
        self.assertIn("2026-04-14", {d["data"] for d in self.cal["locais"]["NOVA XAVANTINA"]})

    def test_todo_dia_tem_tipo_fonte_e_motivo(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        self.assertEqual(ids, {"portaria", "indice"})
        todos = list(self.cal["geral"]) + [x for v in self.cal["locais"].values() for x in v]
        for d in todos:
            self.assertIn(d["tipo"], TIPOS)
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])
            if d["tipo"] == "parcial":
                self.assertTrue(d["horario"])

    def test_numeracao_quebrada_e_erro(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjmt.interpretar((self.texto.replace("\n 2.\n", "\n 3.\n"), self.indice), 2026)

    def test_pdf_de_outro_ano_e_recusado(self) -> None:
        with self.assertRaises(ErroDeFonte):
            tjmt.interpretar((self.texto, self.indice), 2027)

    def test_coletar_baixa_os_dois_e_valida(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [tjmt.URL_PORTARIA[2026], tjmt.URL_INDICE[2026]])
        self.assertEqual(validacao.validar(cal, "TJMT", 2026, self.motor.esperado), [])

    def test_ano_seguinte_ainda_nao_publicado(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])

    def test_parcial_descreve_o_que_ficou_de_fora(self) -> None:
        for trecho in ("509/2026", "901/2026", "752/2026", "recesso"):
            self.assertIn(trecho, self.motor.parcial)


if __name__ == "__main__":
    unittest.main()

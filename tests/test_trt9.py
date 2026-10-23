"""Testes do motor do TRT9. Só usam a FIXTURE (tests/fixtures/trt9/calendario-2026.html), nunca a rede.

A fixture é a página do calendário do portal, guardada em 23/10/2026 (ver docs/fichas/TRT9.md).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.modelo import normalizar_local
from robo.motores import trt9
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trt9", "calendario-2026.html")


def _ler_fixture() -> bytes:
    with open(FIX, "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == trt9.URL:
            return _ler_fixture()
        raise AssertionError("URL fora da fixture: %s" % url)


class TestTRT9(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = trt9.MOTOR
        cls.conteudo = _ler_fixture()
        cls.cal = trt9.interpretar(cls.conteudo, 2026)
        cls.geral = {d["data"]: d for d in cls.cal["geral"]}

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TRT9", 2026, self.motor.esperado), [])

    def test_coletar_passa_pela_rede_e_bate_com_interpretar(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(rede.pedidos, [trt9.URL])
        self.assertEqual(cal["geral"], self.cal["geral"])
        self.assertEqual(cal["locais"], self.cal["locais"])

    def test_ancoras_da_ficha(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)

    def test_contagem(self) -> None:
        # 143 linhas de dados: 46 Nacional + 15 Estadual (geral) e 78 Municipal + 4 Órgão Julgador (locais).
        # Sai uma a menos: 18/02 Quarta-Feira de Cinzas (DUVIDA). Geral = 61 - 1 = 60.
        self.assertEqual(len(self.cal["geral"]), 60)
        self.assertEqual(sum(len(v) for v in self.cal["locais"].values()), 82)
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertGreaterEqual(len(self.cal["locais"]), self.motor.esperado["min_locais"])

    def test_recesso_janeiro_e_dezembro_com_duas_linhas_no_mesmo_dia(self) -> None:
        tipos = {}
        for d in self.cal["geral"]:
            tipos.setdefault(d["data"], set()).add(d["tipo"])
        for n in range(1, 7):
            self.assertIn("recesso", tipos["2026-01-%02d" % n])
        for n in range(20, 32):
            self.assertIn("recesso", tipos["2026-12-%02d" % n])
        # 01/01 e 25/12: recesso + feriado nacional, as duas linhas
        self.assertIn("sem_expediente", tipos["2026-01-01"])
        self.assertIn("sem_expediente", tipos["2026-12-25"])

    def test_suspensao_art_220_janeiro_e_tipo(self) -> None:
        # 07 a 20/01 não é recesso: é suspensão de prazo (Art. 220 CPC, Reg. Interno art. 191 §1º)
        for n in range(7, 21):
            d = self.geral["2026-01-%02d" % n]
            self.assertEqual(d["tipo"], "suspensao_prazo", d)
            self.assertEqual(d["motivo"], "Suspensão de prazo - Art. 220 CPC")
        self.assertEqual(self.geral["2026-01-07"]["fonte"], trt9.FONTE_ID)

    def test_suspensao_avulsa_estadual_vai_para_geral(self) -> None:
        for data in ("2026-01-21", "2026-01-22", "2026-01-23", "2026-06-29",
                     "2026-08-28", "2026-09-01", "2026-09-11"):
            self.assertEqual(self.geral[data]["tipo"], "suspensao_prazo", data)
        # 22/01 também tem o padroeiro de Palotina (unidade): a suspensão continua em geral
        self.assertIn("Dispõe sobre a suspensão", self.geral["2026-01-22"]["motivo"])

    def test_suspensao_de_expediente_e_prazos_vira_sem_expediente(self) -> None:
        for data in ("2026-04-20", "2026-06-05"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente", data)
            self.assertIn("Suspensão de expediente e prazos", self.geral[data]["motivo"])

    def test_18_02_quarta_de_cinzas_nao_entra_por_duvida(self) -> None:
        self.assertNotIn("2026-02-18", self.geral)
        self.assertNotIn("2026-02-18", {d["data"] for v in self.cal["locais"].values() for d in v})

    def test_carnaval_e_feriados_nacionais(self) -> None:
        self.assertEqual(self.geral["2026-02-16"]["motivo"], "Carnaval")
        self.assertEqual(self.geral["2026-02-16"]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-04-21"]["tipo"], "sem_expediente")
        self.assertEqual(self.geral["2026-06-04"]["motivo"], "Corpus Christi")  # tribunal inteiro

    def test_municipal_vai_para_locais_por_origem_com_uf(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["PARANAVAI-PR"]}
        self.assertEqual(dias["2026-01-19"]["tipo"], "sem_expediente")
        # 19/01: o padroeiro de Paranavaí é local; em geral a data é só a suspensão do Art. 220
        self.assertEqual(self.geral["2026-01-19"]["motivo"], "Suspensão de prazo - Art. 220 CPC")
        self.assertIn("CASTRO-PR", self.cal["locais"])  # chave é a Origem com UF, não o nome puro

    def test_suspensao_municipal_de_apucarana_e_local(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["APUCARANA-PR"]}
        for data in ("2026-09-22", "2026-09-23", "2026-09-24"):
            self.assertEqual(dias[data]["tipo"], "suspensao_prazo", data)
            self.assertNotIn(data, self.geral)

    def test_orgao_julgador_fica_em_locais_e_nunca_em_geral(self) -> None:
        palotina = {d["data"]: d for d in self.cal["locais"]["POSTO AVANÇADO DA JUSTIÇA DO TRABALHO DE PALOTINA"]}
        self.assertEqual(palotina["2026-01-22"]["tipo"], "sem_expediente")
        self.assertEqual(palotina["2026-01-22"]["motivo"], "Dia do Padroeiro do Município de Palotina")
        # 22/01 em geral é só a suspensão de prazos 21 a 23/01; o padroeiro não entra em geral
        self.assertNotIn("Padroeiro", self.geral["2026-01-22"]["motivo"])
        self.assertNotIn("2026-07-16", self.geral)
        self.assertIn("VARA DO TRABALHO DE ASSIS CHATEAUBRIAND", self.cal["locais"])

    def test_transferencias_de_feriado_vao_para_geral(self) -> None:
        for data in ("2026-08-14", "2026-10-30", "2026-12-18"):
            self.assertEqual(self.geral[data]["tipo"], "sem_expediente", data)
            self.assertIn("Transferência do feriado", self.geral[data]["motivo"])

    def test_chaves_de_local_normalizadas(self) -> None:
        for nome in self.cal["locais"]:
            self.assertEqual(nome, normalizar_local(nome))

    def test_todo_dia_tem_fonte_valida_e_motivo(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        todos = list(self.cal["geral"]) + [d for v in self.cal["locais"].values() for d in v]
        self.assertTrue(todos)
        for d in todos:
            self.assertIn(d["fonte"], ids)
            self.assertTrue(d["motivo"])
            self.assertNotIn("horario", d)  # a tabela não traz horário: nenhum dia é parcial

    def test_ano_sem_dias_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            trt9.interpretar(self.conteudo, 2027)

    def test_pagina_sem_tabela_levanta_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            trt9.interpretar(b"<html><body>manutencao</body></html>", 2026)


if __name__ == "__main__":
    unittest.main()

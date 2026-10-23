"""Testes do motor do STJ. Só usam as FIXTURES (tests/fixtures/stj), nunca a rede.

horarios_funcionamento_2026.html é a página "Horários de Funcionamento" do STJ, guardada em
23/10/2026; noticia_20_21_abril_2026.html é o comunicado de 16/04/2026 (ver docs/fichas/STJ.md).
"""
from __future__ import annotations

import os
import unittest

from robo import validacao
from robo.modelo import TIPOS, todos_os_dias
from robo.motores import stj
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "stj")


def _ler(nome: str) -> bytes:
    with open(os.path.join(FIX, nome), "rb") as f:
        return f.read()


class TestSTJ(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.motor = stj.MOTOR
        cls.cal = stj.interpretar(_ler("horarios_funcionamento_2026.html"), 2026)
        cls.geral = {}
        for d in cls.cal["geral"]:
            cls.geral.setdefault(d["data"], []).append(d)
        cls.tipos = {}
        for d in cls.cal["geral"]:
            cls.tipos.setdefault(d["data"], set()).add(d["tipo"])

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "STJ", 2026, self.motor.esperado), [])

    def test_contagem_e_um_so_local(self) -> None:
        self.assertEqual(len(self.cal["geral"]), 40)  # 40 dias lidos da tabela de 2026
        self.assertGreaterEqual(len(self.cal["geral"]), self.motor.esperado["min_geral"])
        self.assertEqual(list(self.cal["locais"]), ["BRASÍLIA"])
        self.assertEqual(self.cal["locais"]["BRASÍLIA"], [])

    def test_ancoras(self) -> None:
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertIn(data, self.geral, nome)
        self.assertEqual(self.tipos["2026-02-16"], {"sem_expediente"})
        self.assertEqual(self.tipos["2026-04-21"], {"sem_expediente"})
        self.assertEqual(self.tipos["2026-12-08"], {"sem_expediente"})

    def test_semana_santa_e_carnaval_sao_um_dia_por_data(self) -> None:
        for data in ("2026-02-16", "2026-02-17", "2026-04-01", "2026-04-02", "2026-04-03"):
            self.assertIn(data, self.geral)
        self.assertNotIn("2026-02-18", {d for d in self.geral if self.geral[d][0]["motivo"] == "Carnaval"})

    def test_quarta_de_cinzas_e_parcial_ate_14h(self) -> None:
        d = self.geral["2026-02-18"][0]
        self.assertEqual(d["tipo"], "parcial")
        self.assertEqual(d["horario"], "até as 14h")
        self.assertEqual(len(self.geral["2026-02-18"]), 1)

    def test_pontos_facultativos_viram_sem_expediente(self) -> None:
        for data in ("2026-04-20", "2026-06-04", "2026-06-05", "2026-08-10", "2026-12-07"):
            self.assertEqual(self.tipos[data], {"sem_expediente"}, data)

    def test_7_de_dezembro_ignora_o_rotulo_errado(self) -> None:
        self.assertEqual(self.geral["2026-12-07"][0]["motivo"], "Ponto facultativo")
        self.assertNotIn("Independência do Brasil", [d["motivo"] for d in self.geral["2026-12-07"]])

    def test_recesso_dezembro_e_janeiro(self) -> None:
        for n in range(20, 32):
            self.assertIn("recesso", self.tipos["2026-12-%02d" % n], n)
        for n in range(1, 7):
            self.assertIn("recesso", self.tipos["2026-01-%02d" % n], n)
        self.assertNotIn("2026-01-07", self.geral)

    def test_dia_com_feriado_e_recesso_tem_dois_registros(self) -> None:
        self.assertEqual(self.tipos["2026-01-01"], {"sem_expediente", "recesso"})
        self.assertEqual(self.tipos["2026-12-25"], {"sem_expediente", "recesso"})
        self.assertEqual(len(self.geral["2026-01-01"]), 2)

    def test_nunca_inventa_suspensao_de_prazo(self) -> None:
        self.assertNotIn("suspensao_prazo", {d["tipo"] for d in self.cal["geral"]})

    def test_todo_dia_tem_tipo_fonte_e_motivo(self) -> None:
        ids = {f["id"] for f in self.cal["fontes"]}
        for d in todos_os_dias(self.cal):
            self.assertIn(d["tipo"], TIPOS)
            self.assertTrue(d["motivo"])
            self.assertIn(d["fonte"], ids)

    def test_comunicado_de_abril_confirma_20_e_21(self) -> None:
        comunicado = _ler("noticia_20_21_abril_2026.html").decode("utf-8", "replace")
        self.assertIn("dias 20 e 21", comunicado)
        self.assertIn("2026-04-20", self.geral)
        self.assertIn("2026-04-21", self.geral)

    def test_outro_ano_levanta_ainda_nao_publicado(self) -> None:
        with self.assertRaises(AindaNaoPublicado):
            stj.interpretar(_ler("horarios_funcionamento_2026.html"), 2027)

    def test_pagina_sem_a_tabela_e_erro_de_fonte(self) -> None:
        with self.assertRaises(ErroDeFonte):
            stj.interpretar(b"<html><body>manutencao</body></html>", 2026)


if __name__ == "__main__":
    unittest.main()

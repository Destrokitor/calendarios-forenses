"""Testes do motor do STF. Só usam as FIXTURES (tests/fixtures/stf), nunca a rede.

As fixtures são: calendário 2026 (PDF), Portarias GDG 189/2025, 250/2025, 124/2026, 146/2026 e
112/2026, todas baixadas em 23/10/2026 dos URLs da ficha.
"""
from __future__ import annotations

import datetime
import os
import shutil
import unittest

from robo import validacao
from robo.modelo import todos_os_dias
from robo.motores import stf
from robo.motores.base import AindaNaoPublicado

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "stf")
ARQUIVOS = {
    "calendario": "CalendarioSTFOficial2026.pdf",
    "portaria_189": "portaria_gdg_189_2025.pdf",
    "portaria_250": "portaria_gdg_250_2025_recesso.pdf",
    "portaria_124": "portaria_gdg_124_2026_suspensao_julho.pdf",
    "portaria_146": "portaria_gdg_146_2026_copa.pdf",
    "portaria_112": "portaria_gdg_112_2026_24jun.pdf",
}


def _ler(nome: str) -> bytes:
    with open(os.path.join(FIX, nome), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com a fixture no lugar da internet. Qualquer URL fora da ficha quebra o teste."""

    def __init__(self) -> None:
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        for id_, (furl, _desc) in stf.FONTES.items():
            if url == furl:
                return _ler(ARQUIVOS[id_])
        raise AssertionError("URL fora da fixture: %s" % url)


class TestSTF(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = stf.MOTOR
        textos = {id_: stf.pdf_para_texto(_ler(nome)) for id_, nome in ARQUIVOS.items()}
        cls.cal = stf.interpretar(textos, 2026)
        cls.geral = cls.cal["geral"]

    def _dias(self, data: str, tipo: str = None):
        return [d for d in self.geral if d["data"] == data and (tipo is None or d["tipo"] == tipo)]

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "STF", 2026, self.motor.esperado), [])

    def test_ancoras_da_ficha(self) -> None:
        geral_datas = {d["data"] for d in self.geral}
        for data in self.motor.esperado["ancoras"]:
            self.assertIn(data, geral_datas)
        self.assertEqual(self._dias("2026-02-16")[0]["motivo"], "Carnaval")
        self.assertEqual(self._dias("2026-02-17")[0]["motivo"], "Carnaval")
        self.assertEqual(self._dias("2026-07-02", "suspensao_prazo")[0]["fonte"], "portaria_124")
        self.assertEqual(self._dias("2026-12-20", "recesso")[0]["fonte"], "calendario")

    def test_feriados_de_2026(self) -> None:
        feriados = sorted({d["data"] for d in self.geral if d["tipo"] == "sem_expediente"})
        esperados = [
            "2026-01-01", "2026-02-16", "2026-02-17", "2026-04-01", "2026-04-02", "2026-04-03",
            "2026-04-21", "2026-05-01", "2026-06-29", "2026-08-11", "2026-09-07", "2026-10-12",
            "2026-11-02", "2026-11-20", "2026-12-08", "2026-12-25",
        ]
        # Inclui 29/06 (ponto facultativo com prazo prorrogado, Portaria 146).
        self.assertEqual(feriados, esperados)

    def test_recesso_so_dez_e_jan(self) -> None:
        recesso = sorted(d["data"] for d in self.geral if d["tipo"] == "recesso")
        self.assertEqual(len(recesso), 18)  # 01 a 06/01 (6) e 20 a 31/12 (12)
        self.assertEqual(recesso[0], "2026-01-01")
        self.assertEqual(recesso[-1], "2026-12-31")
        self.assertTrue(all(d.startswith(("2026-01", "2026-12")) for d in recesso))

    def test_suspensoes_jan_e_jul(self) -> None:
        susp = [d["data"] for d in self.geral if d["tipo"] == "suspensao_prazo"]
        jan = [d for d in susp if d.startswith("2026-01")]
        jul = [d for d in susp if d.startswith("2026-07")]
        self.assertEqual(len(jan), 31)  # Portaria 250, art. 4º: 20/12/2025 a 31/01/2026
        self.assertEqual(len(jul), 30)  # Portaria 124, art. 1º: 2 a 31/07/2026
        self.assertEqual(len(susp), len(jan) + len(jul))
        self.assertEqual(self._dias("2026-07-01"), [])  # 1º de julho não está suspenso

    def test_dia_01_01_tem_tres_registros(self) -> None:
        # Feriado + recesso + suspensão de prazos no mesmo dia: a chave é o conjunto, não a data.
        tipos = {d["tipo"] for d in self._dias("2026-01-01")}
        self.assertEqual(tipos, {"sem_expediente", "recesso", "suspensao_prazo"})

    def test_expediente_parcial_e_reduzido(self) -> None:
        cinzas = self._dias("2026-02-18")
        self.assertEqual(len(cinzas), 1)
        self.assertEqual(cinzas[0]["tipo"], "parcial")
        self.assertEqual(cinzas[0]["horario"], "até as 14h")
        reduzido = self._dias("2026-06-24")
        self.assertEqual(len(reduzido), 1)
        self.assertEqual(reduzido[0]["tipo"], "parcial")
        self.assertEqual(reduzido[0]["horario"], "das 11h às 18h")

    def test_pontos_facultativos_nao_lancados(self) -> None:
        # DUVIDA da ficha: efeito sobre prazo não definido na fonte. Não viram dia (ver docstring do motor).
        for data in ("2026-04-20", "2026-06-04", "2026-06-05", "2026-08-10", "2026-10-30", "2026-12-07"):
            self.assertEqual(self._dias(data), [], data)

    def test_locais_chave_unica(self) -> None:
        self.assertEqual(self.cal["locais"], {"BRASÍLIA": []})

    def test_todo_dia_tem_fonte_e_tipo_valido(self) -> None:
        ids = set(stf.FONTES)
        for d in todos_os_dias(self.cal):
            self.assertIn(d["fonte"], ids)
            self.assertIn(d["tipo"], ("sem_expediente", "recesso", "suspensao_prazo", "parcial"))

    def test_coletar_2026_usa_so_as_urls_da_ficha(self) -> None:
        rede = RedeFalsa()
        cal = self.motor.coletar(2026, rede)
        self.assertEqual(len(rede.pedidos), len(stf.FONTES))
        self.assertEqual(len(cal["geral"]), len(self.geral))

    def test_2027_ainda_nao_publicado(self) -> None:
        rede = RedeFalsa()
        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, rede)
        self.assertEqual(rede.pedidos, [])


if __name__ == "__main__":
    unittest.main()

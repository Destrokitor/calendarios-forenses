"""Testes do motor do TJSP. Só usam as FIXTURES (tests/fixtures/tjsp), nunca a rede.

A fixture da consulta pública (consulta-2026.json) é a resposta real dos dois endereços JSON
do portal para cada comarca, guardada em 23/10/2026.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import unittest
import urllib.parse

from robo import validacao
from robo.motores import tjsp
from robo.motores.base import AindaNaoPublicado
from robo.rede import ErroDeFonte

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tjsp")


def _ler(nome: str) -> bytes:
    with open(os.path.join(FIX, nome), "rb") as f:
        return f.read()


class RedeFalsa:
    """Responde com as fixtures no lugar da internet."""

    def __init__(self) -> None:
        self.consulta = json.loads(_ler("consulta-2026.json").decode("utf-8"))
        self.pedidos = []

    def baixar(self, url: str) -> bytes:
        self.pedidos.append(url)
        if url == tjsp.URL_ANOS:
            return _ler("anos.html")
        if url == tjsp.URL_COMARCAS:
            return _ler("comarcas-raj.html")
        if url == tjsp.PROVIMENTOS[2026]:
            return _ler("provimento-csm-2813-2025.pdf")
        for base, campo in ((tjsp.URL_FERIADOS, "feriados"), (tjsp.URL_SUSPENSOES, "suspensoes")):
            if url.startswith(base + "?"):
                q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
                assert q["ano"] == ["2026"]
                reg = self.consulta.get(q["nomeMunicipio"][0])
                resposta = reg[campo] if reg else {"data": []}  # nome que o portal não conhece
                return json.dumps(resposta).encode("utf-8")
        raise AssertionError("URL fora das fixtures: %s" % url)


def _datas(dias):
    return {d["data"] for d in dias}


class TestTJSP(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("pdftotext"):
            raise unittest.SkipTest("pdftotext não instalado")
        cls.motor = tjsp.MOTOR
        cls.cal = cls.motor.coletar(2026, RedeFalsa())

    def test_valida(self) -> None:
        self.assertEqual(validacao.validar(self.cal, "TJSP", 2026, self.motor.esperado), [])

    def test_ancoras_e_tipos(self) -> None:
        geral = {d["data"]: d for d in self.cal["geral"]}
        for data, nome in self.motor.esperado["ancoras"].items():
            self.assertEqual(geral[data]["tipo"], "sem_expediente", nome)
        self.assertIn("CARNAVAL", geral["2026-02-16"]["motivo"])
        self.assertIn("SEXTA-FEIRA DA PAIXÃO", geral["2026-04-03"]["motivo"])
        self.assertIn("DIA DA JUSTIÇA", geral["2026-12-08"]["motivo"])

    def test_recesso_e_suspensao_de_janeiro_e_dezembro(self) -> None:
        geral = {d["data"]: d for d in self.cal["geral"]}
        for n in range(1, 7):
            self.assertEqual(geral["2026-01-%02d" % n]["tipo"], "recesso")
        for n in range(7, 21):  # 07 a 20/01: prazos suspensos (RITJSP art. 116 §2º), fórum abre
            self.assertEqual(geral["2026-01-%02d" % n]["tipo"], "suspensao_prazo")
        self.assertNotIn("2026-01-21", geral)
        for n in range(20, 32):
            self.assertEqual(geral["2026-12-%02d" % n]["tipo"], "recesso")
            self.assertEqual(geral["2026-12-%02d" % n]["fonte"], "provimento")

    def test_dia_do_servidor_foi_movido_de_28_para_30_de_outubro(self) -> None:
        # O PDF do provimento diz 28/10; a consulta pública (mais nova) traz a alteração.
        geral = {d["data"]: d for d in self.cal["geral"]}
        self.assertNotIn("2026-10-28", geral)
        self.assertIn("DIA DO SERVIDOR", geral["2026-10-30"]["motivo"])
        self.assertIn("2845", geral["2026-10-30"]["motivo"])

    def test_quarta_de_cinzas_e_dia_parcial(self) -> None:
        d = [x for x in self.cal["geral"] if x["data"] == "2026-02-18"]
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0]["tipo"], "parcial")
        self.assertEqual(d[0]["horario"], "a partir das 13h")

    def test_contagens(self) -> None:
        self.assertGreaterEqual(len(self.cal["geral"]), 40)
        self.assertEqual(len(self.cal["locais"]), 320)  # 321 da lista menos Vila Mimosa
        self.assertNotIn("VILA MIMOSA", self.cal["locais"])
        # toda comarca entra, mesmo sem dia próprio (lista vazia é válida)
        self.assertTrue(all(isinstance(v, list) for v in self.cal["locais"].values()))

    def test_nenhum_dia_municipal_vazou_para_o_geral(self) -> None:
        for d in self.cal["geral"]:
            if d["fonte"] == "portal" and d["tipo"] == "sem_expediente":
                self.assertTrue("PROVIMENTO" in d["motivo"].upper() or d["data"] in ("2026-12-08",), d)
        self.assertNotIn("2026-06-13", _datas(self.cal["geral"]))  # Santo Antônio de Americana etc.

    def test_local_adamantina(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["ADAMANTINA"]}
        self.assertEqual(sorted(dias), ["2026-06-13"])  # 08/12 já é do provimento (geral)
        self.assertEqual(dias["2026-06-13"]["tipo"], "sem_expediente")
        self.assertEqual(dias["2026-06-13"]["fonte"], "portal")

    def test_local_com_dia_parcial(self) -> None:
        dias = {d["data"]: d for d in self.cal["locais"]["ANDRADINA"]}
        self.assertEqual(dias["2026-08-06"]["tipo"], "parcial")
        self.assertEqual(dias["2026-08-06"]["horario"], "a partir das 12h")

    def test_local_so_com_o_estado_fica_vazio_mas_existe(self) -> None:
        vazios = [k for k, v in self.cal["locais"].items() if not v]
        self.assertGreater(len(vazios), 0)  # comarcas cujos feriados coincidem com os do provimento
        self.assertLess(len(vazios), 60)
        for k in vazios:
            self.assertIn(k, self.cal["locais"])

    def test_nomes_com_grafia_diferente_da_lista_de_comarcas(self) -> None:
        for chave in ("CARAPICUÍBA", "ESTRELA DOESTE", "SÃO LUIZ DO PARAITINGA", "SANTA BÁRBARA D'OESTE",
                      "RIO GRANDE DA SERRA", "SANTANA DE PARNAÍBA", "MOGI GUAÇU", "SÃO PAULO"):
            self.assertIn(chave, self.cal["locais"])
            self.assertTrue(chave == chave.upper())

    def test_capital_tem_a_fundacao_de_sao_paulo(self) -> None:
        self.assertIn("2026-01-25", _datas(self.cal["locais"]["SÃO PAULO"]))

    def test_comunicados_de_unidade_ficam_de_fora(self) -> None:
        for lista in self.cal["locais"].values():
            for d in lista:
                self.assertNotIn("COMUNICADO", d["motivo"].upper())
        self.assertIn("comunicado", self.motor.parcial.lower())

    def test_confere_com_o_texto_do_provimento(self) -> None:
        """Todo dia do art. 1º do provimento está no resultado, salvo o 28/10 (alterado)."""
        texto = " ".join(tjsp.pdf_para_texto(_ler("provimento-csm-2813-2025.pdf")).split())
        art1 = texto[texto.index("Art. 1º - No exercício de 2026"):texto.index("§ 1º - Também")]
        achados = re.findall(r"(\d{1,2})º? de (\w+) – [\w-]+ – ", art1)
        self.assertEqual(len(achados), 18)
        datas = {datetime.date(2026, tjsp._MESES[m], int(d)).isoformat() for d, m in achados}
        geral = _datas(self.cal["geral"])
        self.assertEqual(datas - geral, {"2026-10-28"})
        self.assertEqual(geral - datas - {d for d in geral if d.startswith(("2026-01", "2026-12"))}
                         - {"2026-02-18", "2026-10-30"}, set())

    def test_datas_moveis_batem_com_a_pascoa(self) -> None:
        p = tjsp.pascoa(2026)
        self.assertEqual(p, datetime.date(2026, 4, 5))
        geral = _datas(self.cal["geral"])
        for dias, nome in ((-48, "carnaval"), (-47, "carnaval"), (-2, "sexta-feira da paixão"), (60, "corpus christi")):
            self.assertIn((p + datetime.timedelta(days=dias)).isoformat(), geral, nome)
        self.assertEqual(tjsp.pascoa(2027), datetime.date(2027, 3, 28))

    def test_ano_seguinte_ainda_nao_publicado(self) -> None:
        class Rede2027(RedeFalsa):
            def baixar(self, url: str) -> bytes:
                return _ler("anos.html") if url == tjsp.URL_ANOS else super().baixar(url)

        with self.assertRaises(AindaNaoPublicado):
            self.motor.coletar(2027, Rede2027())

    def test_ano_sem_provimento_cadastrado_usa_a_lei_para_dezembro(self) -> None:
        feriados = {k: v["feriados"]["data"] for k, v in RedeFalsa().consulta.items()}
        suspensoes = {k: v["suspensoes"]["data"] for k, v in RedeFalsa().consulta.items()}
        cal = self.motor.montar(2026, feriados, suspensoes, None)
        dez = [d for d in cal["geral"] if d["data"] >= "2026-12-20"]
        self.assertEqual(len(dez), 12)
        self.assertTrue(all(d["tipo"] == "suspensao_prazo" and d["fonte"] == "cpc-220" for d in dez))
        self.assertEqual(validacao.validar(cal, "TJSP", 2026, self.motor.esperado), [])

    def test_provimento_de_outro_ano_e_recusado(self) -> None:
        texto = tjsp.pdf_para_texto(_ler("provimento-csm-2813-2025.pdf"))
        with self.assertRaises(ErroDeFonte):
            tjsp.ler_provimento(texto, 2027)

    def test_horario_parcial(self) -> None:
        self.assertEqual(tjsp._horario("A PARTIR DAS 12 HORAS - PROCISSÃO"), "a partir das 12h")
        self.assertEqual(tjsp._horario("ATÉ AS 11 HORAS"), "até as 11h")
        self.assertEqual(tjsp._horario("NOSSA SENHORA DAS GRAÇAS"), "")


if __name__ == "__main__":
    unittest.main()

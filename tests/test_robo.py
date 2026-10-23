import datetime
import json
import os
import tempfile
import unittest

from robo.executar import executar
from robo.modelo import calendario_vazio, dia
from robo.motores.base import AindaNaoPublicado, Motor
from robo.registro import todos_os_tribunais
from robo.validacao import validar
from robo import vigia

HOJE = datetime.date(2026, 10, 24)


def calendario_bom(sigla="TJSP", ano=2026):
    cal = calendario_vazio(sigla, ano)
    cal["fontes"] = [{"id": "f1", "url": "https://exemplo.invalid", "descricao": "teste"}]
    cal["geral"] = [
        dia(datetime.date(ano, 2, 16), "sem_expediente", "Carnaval", "f1"),
        dia(datetime.date(ano, 10, 28), "sem_expediente", "Dia do Servidor", "f1"),
        dia(datetime.date(ano, 12, 21), "recesso", "Recesso", "f1"),
    ]
    cal["locais"] = {"AGUAÍ": [dia(datetime.date(ano, 8, 6), "sem_expediente", "Feriado municipal", "f1")], "ADAMANTINA": []}
    return cal


class MotorBom(Motor):
    sigla = "TJSP"
    esperado = {"min_geral": 3, "min_locais": 2, "ancoras": {"2026-10-28": "Dia do Servidor"}, "exige_recesso": True}

    def anos(self, hoje):
        return [hoje.year]

    def coletar(self, ano, rede):
        return calendario_bom("TJSP", ano)


class MotorQuebrado(MotorBom):
    def coletar(self, ano, rede):
        raise RuntimeError("site fora do ar")


class MotorLidoPelaMetade(MotorBom):
    def coletar(self, ano, rede):
        cal = calendario_bom("TJSP", ano)
        cal["geral"] = cal["geral"][:1]
        return cal


class MotorAnoQueVem(MotorBom):
    def anos(self, hoje):
        return [hoje.year, hoje.year + 1]

    def coletar(self, ano, rede):
        if ano > HOJE.year:
            raise AindaNaoPublicado()
        return calendario_bom("TJSP", ano)


class MotorIpBrasil(MotorBom):
    sigla = "TJMG"
    precisa_ip_brasil = True

    def coletar(self, ano, rede):
        return calendario_bom("TJMG", ano)


class Registro(unittest.TestCase):
    def test_sao_92_tribunais_sem_repeticao(self):
        siglas = [t["sigla"] for t in todos_os_tribunais()]
        self.assertEqual(len(siglas), 92)
        self.assertEqual(len(set(siglas)), 92)
        for s in ("STF", "STJ", "TST", "TSE", "STM", "TJSP", "TJDFT", "TJMSP", "TRF6", "TRT24", "TREDF"):
            self.assertIn(s, siglas)


class Validacao(unittest.TestCase):
    ESP = MotorBom.esperado

    def test_calendario_bom_passa(self):
        self.assertEqual(validar(calendario_bom(), "TJSP", 2026, self.ESP), [])

    def test_data_fora_do_ano(self):
        cal = calendario_bom()
        cal["geral"].append(dia(datetime.date(2027, 1, 1), "sem_expediente", "X", "f1"))
        self.assertTrue(any("fora do ano" in e for e in validar(cal, "TJSP", 2026, self.ESP)))

    def test_ancora_ausente(self):
        cal = calendario_bom()
        cal["geral"] = [d for d in cal["geral"] if d["data"] != "2026-10-28"]
        self.assertTrue(any("âncora" in e for e in validar(cal, "TJSP", 2026, self.ESP)))

    def test_sem_recesso(self):
        cal = calendario_bom()
        cal["geral"] = [d for d in cal["geral"] if d["tipo"] != "recesso"]
        self.assertTrue(any("recesso" in e for e in validar(cal, "TJSP", 2026, self.ESP)))

    def test_parcial_exige_horario(self):
        cal = calendario_bom()
        cal["geral"].append(dia(datetime.date(2026, 8, 6), "parcial", "Meio dia", "f1"))
        self.assertTrue(any("horário" in e for e in validar(cal, "TJSP", 2026, self.ESP)))

    def test_fonte_inexistente_e_tribunal_errado(self):
        cal = calendario_bom("TJRJ")
        cal["geral"][0]["fonte"] = "nao-existe"
        erros = validar(cal, "TJSP", 2026, self.ESP)
        self.assertTrue(any("tribunal no arquivo" in e for e in erros))
        self.assertTrue(any("fonte inexistente" in e for e in erros))

    def test_local_fora_do_padrao_e_poucos_locais(self):
        cal = calendario_bom()
        cal["locais"] = {"aguaí": []}
        erros = validar(cal, "TJSP", 2026, self.ESP)
        self.assertTrue(any("fora do padrão" in e for e in erros))
        self.assertTrue(any("poucos locais" in e for e in erros))


class Robo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, motores, **kw):
        return executar(self.raiz, {m.sigla: m for m in motores}, HOJE, rede=None, **kw)

    def cobertura(self):
        with open(os.path.join(self.raiz, "dados", "cobertura.json"), encoding="utf-8") as f:
            return json.load(f)

    def texto(self):
        with open(self.arquivo(), encoding="utf-8") as f:
            return f.read()

    def arquivo(self, sigla="TJSP", ano=2026):
        return os.path.join(self.raiz, "dados", sigla, "%d.json" % ano)

    def test_grava_e_marca_verificado(self):
        r = self.rodar([MotorBom()])
        self.assertEqual(r["falhas"], [])
        self.assertTrue(os.path.exists(self.arquivo()))
        cob = self.cobertura()
        self.assertEqual(cob["tribunais"]["TJSP"]["status"], "verificado")
        self.assertEqual(cob["tribunais"]["TJSP"]["anos"]["2026"]["locais"], 2)
        self.assertEqual(cob["tribunais"]["STF"]["status"], "sem_motor")
        self.assertEqual(len(cob["tribunais"]), 92)

    def test_conteudo_igual_nao_reescreve_o_arquivo(self):
        self.rodar([MotorBom()])
        antes = self.texto()
        self.rodar([MotorBom()])
        self.assertEqual(self.texto(), antes)

    def test_falha_mantem_dado_antigo_e_marca_desatualizado(self):
        self.rodar([MotorBom()])
        antes = self.texto()
        r = self.rodar([MotorQuebrado()])
        self.assertEqual(self.texto(), antes)
        self.assertEqual(len(r["falhas"]), 1)
        t = self.cobertura()["tribunais"]["TJSP"]
        self.assertEqual(t["status"], "desatualizado")
        self.assertIn("site fora do ar", t["anos"]["2026"]["erro"])
        self.assertTrue(t["anos"]["2026"]["ultima_ok"])

    def test_falha_sem_dado_anterior_e_indisponivel(self):
        self.rodar([MotorQuebrado()])
        self.assertEqual(self.cobertura()["tribunais"]["TJSP"]["status"], "indisponivel")
        self.assertFalse(os.path.exists(self.arquivo()))

    def test_calendario_lido_pela_metade_nao_e_gravado(self):
        r = self.rodar([MotorLidoPelaMetade()])
        self.assertFalse(os.path.exists(self.arquivo()))
        self.assertEqual(len(r["falhas"]), 1)
        self.assertEqual(self.cobertura()["tribunais"]["TJSP"]["status"], "indisponivel")

    def test_ano_que_vem_ainda_nao_publicado_nao_e_falha(self):
        r = self.rodar([MotorAnoQueVem()])
        self.assertEqual(r["falhas"], [])
        anos = self.cobertura()["tribunais"]["TJSP"]["anos"]
        self.assertTrue(anos["2027"]["nao_publicado"])
        self.assertEqual(self.cobertura()["tribunais"]["TJSP"]["status"], "verificado")

    def test_grupos_separam_quem_precisa_de_ip_brasileiro(self):
        self.rodar([MotorBom(), MotorIpBrasil()], grupo="geral")
        self.assertTrue(os.path.exists(self.arquivo()))
        self.assertFalse(os.path.exists(self.arquivo("TJMG")))
        self.rodar([MotorBom(), MotorIpBrasil()], grupo="brasil")
        self.assertTrue(os.path.exists(self.arquivo("TJMG")))

    def test_uma_falha_nao_derruba_os_outros_e_preserva_cobertura_alheia(self):
        self.rodar([MotorBom(), MotorIpBrasil()])
        self.rodar([MotorQuebrado(), MotorIpBrasil()], grupo="geral")  # TJMG não roda; deve manter o estado
        cob = self.cobertura()["tribunais"]
        self.assertEqual(cob["TJMG"]["status"], "verificado")
        self.assertEqual(cob["TJSP"]["status"], "desatualizado")

    def test_parcial(self):
        class MotorParcial(MotorBom):
            parcial = "só feriados do anexo; portarias locais ficam de fora"
        self.rodar([MotorParcial()])
        t = self.cobertura()["tribunais"]["TJSP"]
        self.assertEqual(t["status"], "parcial")
        self.assertIn("portarias locais", t["observacao"])


class MotorSemAncora(MotorBom):
    esperado = {"min_geral": 3, "min_locais": 2, "exige_recesso": True}


class Vigia(unittest.TestCase):
    def test_vigia(self):
        hoje = datetime.date.today()  # o vigia usa o ano do relógio; o teste acompanha
        with tempfile.TemporaryDirectory() as raiz:
            agora = datetime.datetime.now(datetime.timezone.utc)
            self.assertTrue(vigia.verificar(raiz, agora))  # nunca rodou
            executar(raiz, {"TJSP": MotorSemAncora()}, hoje, rede=None)
            self.assertEqual(vigia.verificar(raiz, agora + datetime.timedelta(hours=3)), [])
            problemas = vigia.verificar(raiz, agora + datetime.timedelta(days=3))
            self.assertTrue(any("parou de rodar" in p for p in problemas))
            self.assertTrue(any("TJSP" in p for p in problemas))


if __name__ == "__main__":
    unittest.main()

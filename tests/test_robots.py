import unittest

from robo.robots import permitido

AG = "calendarios-forenses-robo"


class Robots(unittest.TestCase):
    def test_mais_especifico_vence_como_na_rfc(self):
        # caso real (TJSE): Disallow: / seguido de Allow: /portal
        txt = "User-agent: *\nDisallow: /\nAllow: /portal\n"
        self.assertTrue(permitido(txt, AG, "/portal/arquivos/calendario.pdf"))
        self.assertFalse(permitido(txt, AG, "/admin"))

    def test_disallow_total_continua_valendo(self):
        self.assertFalse(permitido("User-agent: *\nDisallow: /\n", AG, "/qualquer"))

    def test_grupo_proprio_do_robo_tem_prioridade_sobre_asterisco(self):
        txt = "User-agent: *\nDisallow: /\n\nUser-agent: calendarios-forenses-robo\nAllow: /\n"
        self.assertTrue(permitido(txt, AG, "/x"))
        txt2 = "User-agent: *\nAllow: /\n\nUser-agent: calendarios-forenses-robo\nDisallow: /privado\n"
        self.assertFalse(permitido(txt2, AG, "/privado/a"))
        self.assertTrue(permitido(txt2, AG, "/publico"))

    def test_empate_vence_allow_e_disallow_vazio_libera(self):
        self.assertTrue(permitido("User-agent: *\nDisallow: /a\nAllow: /a\n", AG, "/a"))
        self.assertTrue(permitido("User-agent: *\nDisallow:\n", AG, "/qualquer"))

    def test_curinga_e_fim_de_linha(self):
        txt = "User-agent: *\nDisallow: /*.json$\n"
        self.assertFalse(permitido(txt, AG, "/dados/a.json"))
        self.assertTrue(permitido(txt, AG, "/dados/a.json?x=1"))
        self.assertTrue(permitido(txt, AG, "/dados/a.pdf"))

    def test_sem_regras_ou_sem_grupo_aplicavel_libera(self):
        self.assertTrue(permitido("", AG, "/x"))
        self.assertTrue(permitido("User-agent: outrobot\nDisallow: /\n", AG, "/x"))

    def test_comentarios_e_caixa(self):
        txt = "USER-AGENT: *  # todos\nDISALLOW: /privado # só isto\n"
        self.assertFalse(permitido(txt, AG, "/privado/x"))
        self.assertTrue(permitido(txt, AG, "/publico"))


if __name__ == "__main__":
    unittest.main()

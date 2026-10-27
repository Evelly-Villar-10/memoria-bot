from django.test import TestCase

from .regras import (
    Carta, criar_tabuleiro, formam_par, novo_estado,
    posicoes_livres, resolver_par, resultado,
)


class RegrasTest(TestCase):
    def test_tabuleiro_tem_24_cartas_diferentes(self):
        cartas = criar_tabuleiro()
        self.assertEqual(len(cartas), 24)
        self.assertEqual(len(set(cartas)), 24)

    def test_cada_valor_aparece_duas_vezes_formando_par(self):
        por_valor = {}
        for c in criar_tabuleiro():
            por_valor.setdefault(c.valor, []).append(c)
        self.assertEqual(len(por_valor), 12)
        for grupo in por_valor.values():
            self.assertEqual(len(grupo), 2)
            self.assertTrue(formam_par(grupo[0], grupo[1]))

    def test_mesma_cor_forma_par(self):
        self.assertTrue(formam_par(Carta(7, "H"), Carta(7, "D")))
        self.assertTrue(formam_par(Carta(7, "S"), Carta(7, "C")))

    def test_cores_diferentes_nao_formam_par(self):
        self.assertFalse(formam_par(Carta(7, "H"), Carta(7, "S")))

    def test_valores_diferentes_nao_formam_par(self):
        self.assertFalse(formam_par(Carta(7, "H"), Carta(8, "H")))

    def test_carta_nao_forma_par_com_ela_mesma(self):
        carta = Carta(7, "H")
        self.assertFalse(formam_par(carta, carta))

    def test_codigo_ida_e_volta(self):
        carta = Carta(12, "H")
        self.assertEqual(carta.codigo, "12H")
        self.assertEqual(Carta.de_codigo("12H"), carta)

    def test_novo_estado(self):
        estado = novo_estado()
        self.assertEqual(len(estado["cartas"]), 24)
        self.assertEqual(len(posicoes_livres(estado)), 24)
        self.assertEqual(estado["placar"], {"jogador": 0, "bot": 0})

    def test_resolver_par(self):
        estado = novo_estado()
        estado["memoria_bot"] = {"0": "1H", "1": "1D", "5": "9S"}
        resolver_par(estado, 0, 1, "jogador")
        self.assertEqual(estado["dono"][0], "jogador")
        self.assertEqual(estado["dono"][1], "jogador")
        self.assertEqual(estado["placar"]["jogador"], 1)
        self.assertEqual(estado["memoria_bot"], {"5": "9S"})
        self.assertEqual(len(posicoes_livres(estado)), 22)

    def test_resultado(self):
        estado = novo_estado()
        estado["placar"] = {"jogador": 7, "bot": 5}
        self.assertEqual(resultado(estado), "vitoria")
        estado["placar"] = {"jogador": 4, "bot": 8}
        self.assertEqual(resultado(estado), "derrota")
        estado["placar"] = {"jogador": 6, "bot": 6}
        self.assertEqual(resultado(estado), "empate")
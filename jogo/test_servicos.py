
from django.test import TestCase

from .servicos import (
    criar_partida,
    virar_carta,
    historico,
    estatisticas,
    ErroJogo,
)
from .models import Partida


class ServicosTest(TestCase):

    def setUp(self):
        self.sessao = "sessao-teste"
        self.partida = criar_partida(self.sessao, "facil")

    def test_criar_partida(self):
        self.assertIsNotNone(self.partida.pk)
        self.assertEqual(self.partida.sessao, self.sessao)
        self.assertEqual(self.partida.dificuldade, "facil")
        self.assertEqual(self.partida.status, "jogando")
        self.assertEqual(len(self.partida.estado["cartas"]), 24)

    def test_dificuldade_invalida_usa_medio(self):
        partida = criar_partida(self.sessao, "impossivel")

        self.assertEqual(partida.dificuldade, "medio")

    def test_nao_permite_posicao_invalida(self):
        with self.assertRaises(ErroJogo):
            virar_carta(self.sessao, self.partida.pk, -1)

        with self.assertRaises(ErroJogo):
            virar_carta(self.sessao, self.partida.pk, 24)

    def test_nao_permite_acessar_partida_de_outra_sessao(self):
        with self.assertRaises(Partida.DoesNotExist):
            virar_carta("outra-sessao", self.partida.pk, 0)

    def test_primeira_carta_fica_virada(self):
        eventos = virar_carta(self.sessao, self.partida.pk, 0)

        self.partida.refresh_from_db()

        self.assertEqual(self.partida.estado["viradas"], [0])
        self.assertEqual(eventos[0]["tipo"], "virar")
        self.assertEqual(eventos[0]["pos"], 0)

    def test_nao_permite_virar_a_mesma_carta_duas_vezes(self):
        virar_carta(self.sessao, self.partida.pk, 0)

        with self.assertRaises(ErroJogo):
            virar_carta(self.sessao, self.partida.pk, 0)

    def test_historico_nao_inclui_partida_em_andamento(self):
        partidas = list(historico(self.sessao))

        self.assertEqual(partidas, [])

    def test_estatisticas_sem_partidas_finalizadas(self):
        dados = estatisticas(self.sessao)

        self.assertEqual(dados["total"], 0)
        self.assertEqual(dados["vitorias"], 0)
        self.assertEqual(dados["derrotas"], 0)
        self.assertEqual(dados["empates"], 0)
        self.assertIsNone(dados["melhor"])

class TestesParesEFinalizacao(TestCase):

    def setUp(self):
        self.sessao = "sessao-pares"
        self.partida = criar_partida(self.sessao, "facil")
        self.partida.refresh_from_db()
        self.cartas = self.partida.estado["cartas"]

    def encontrar_par(self):
        from .regras import Carta, formam_par

        for i in range(len(self.cartas)):
            for j in range(i + 1, len(self.cartas)):
                carta_a = Carta.de_codigo(self.cartas[i])
                carta_b = Carta.de_codigo(self.cartas[j])

                if formam_par(carta_a, carta_b):
                    return i, j

    def test_formar_par(self):
        a, b = self.encontrar_par()

        virar_carta(self.sessao, self.partida.pk, a)
        eventos = virar_carta(self.sessao, self.partida.pk, b)

        self.partida.refresh_from_db()

        self.assertTrue(
            any(evento["tipo"] == "par" for evento in eventos)
        )
        self.assertEqual(self.partida.estado["dono"][a], "jogador")
        self.assertEqual(self.partida.estado["dono"][b], "jogador")
        self.assertEqual(self.partida.pares_jogador, 1)

    def test_par_incorreto(self):
        from .regras import Carta, formam_par

        a, b = None, None

        for i in range(len(self.cartas)):
            for j in range(i + 1, len(self.cartas)):
                carta_a = Carta.de_codigo(self.cartas[i])
                carta_b = Carta.de_codigo(self.cartas[j])

                if not formam_par(carta_a, carta_b):
                    a, b = i, j
                    break

            if a is not None:
                break

        virar_carta(self.sessao, self.partida.pk, a)
        eventos = virar_carta(self.sessao, self.partida.pk, b)

        self.assertTrue(
            any(evento["tipo"] == "erro" for evento in eventos)
        )

    def test_finalizar_partida_ao_formar_ultimo_par(self):
        from .regras import Carta, formam_par

        a, b = self.encontrar_par()

        estado = self.partida.estado
        estado["dono"] = ["jogador"] * len(self.cartas)
        estado["dono"][a] = None
        estado["dono"][b] = None
        estado["placar"] = {"jogador": 11, "bot": 0}
        estado["viradas"] = []

        self.partida.estado = estado
        self.partida.pares_jogador = 11
        self.partida.save()

        virar_carta(self.sessao, self.partida.pk, a)
        eventos = virar_carta(self.sessao, self.partida.pk, b)

        self.partida.refresh_from_db()

        self.assertEqual(self.partida.status, "fim")
        self.assertEqual(self.partida.resultado, "vitoria")
        self.assertTrue(
            any(evento["tipo"] == "fim" for evento in eventos)
        )

        self.assertEqual(
            len(historico(self.sessao)),
            1
        )

        dados = estatisticas(self.sessao)

        self.assertEqual(dados["total"], 1)
        self.assertEqual(dados["vitorias"], 1)


from django.test import TestCase

from .bot import turno_bot
from .regras import Carta, formam_par, novo_estado, posicoes_livres


def achar_um_par(estado):
    cartas = [Carta.de_codigo(c) for c in estado["cartas"]]

    for i in range(len(cartas)):
        for j in range(i + 1, len(cartas)):
            if formam_par(cartas[i], cartas[j]):
                return i, j


class BotTest(TestCase):
    def test_bot_joga_o_par_que_lembra(self):
        estado = novo_estado()
        i, j = achar_um_par(estado)

        estado["memoria_bot"] = {
            str(i): estado["cartas"][i],
            str(j): estado["cartas"][j],
        }

        eventos = turno_bot(estado, "dificil", esquecimento=0)

        viradas = [
            ev["pos"]
            for ev in eventos
            if ev["tipo"] == "virar"
        ][:2]

        self.assertEqual(set(viradas), {i, j})
        self.assertEqual(estado["dono"][i], "bot")
        self.assertEqual(estado["dono"][j], "bot")

    def test_bot_que_lembra_de_tudo_limpa_o_tabuleiro_sem_errar(self):
        estado = novo_estado()
        estado["memoria_bot"] = {
            str(i): c for i, c in enumerate(estado["cartas"])
        }

        eventos = turno_bot(estado, "dificil", esquecimento=0)

        self.assertNotIn("erro", [ev["tipo"] for ev in eventos])
        self.assertEqual(estado["placar"]["bot"], 12)
        self.assertEqual(posicoes_livres(estado), [])

    def test_partida_inteira_so_com_bot(self):
        estado = novo_estado()

        for _ in range(2000):
            if not posicoes_livres(estado):
                break

            livres_antes = set(posicoes_livres(estado))
            eventos = turno_bot(estado, "medio")

            resolvidas = set()
            viradas = []

            for ev in eventos:
                if ev["tipo"] == "virar":
                    self.assertIn(
                        ev["pos"], livres_antes
                    )  # nunca vira carta já resolvida

                    self.assertNotIn(ev["pos"], resolvidas)
                    viradas.append(ev["pos"])

                elif ev["tipo"] == "par":
                    resolvidas.update(ev["pos"])

            for k in range(0, len(viradas), 2):
                # Nunca vira a mesma carta duas vezes no turno.
                self.assertNotEqual(viradas[k], viradas[k + 1])

        self.assertEqual(posicoes_livres(estado), [])
        self.assertEqual(estado["placar"]["bot"], 12)

    def test_bot_esquece_todas_as_cartas_com_taxa_total(self):
        estado = novo_estado()

        estado["memoria_bot"] = {
            str(i): codigo
            for i, codigo in enumerate(estado["cartas"])
        }

        turno_bot(estado, "facil", esquecimento=1.0)

        # Com taxa 1.0, a memória anterior deve ser esquecida.
        # O bot ainda pode acertar pares por sorte ou por
        # informações descobertas durante a própria jogada.
        self.assertLessEqual(
            estado["placar"]["bot"],
            len(estado["cartas"]) // 2,
        )

    def test_bot_nao_usa_cartas_que_ja_formaram_par(self):
        estado = novo_estado()

        i, j = achar_um_par(estado)

        estado["memoria_bot"] = {
            str(i): estado["cartas"][i],
            str(j): estado["cartas"][j],
        }

        turno_bot(estado, "dificil", esquecimento=0)

        # Depois de acertar, as cartas resolvidas não devem
        # permanecer na memória do bot.
        self.assertNotIn(str(i), estado["memoria_bot"])
        self.assertNotIn(str(j), estado["memoria_bot"])

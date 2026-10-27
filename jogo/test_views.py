import json

from django.test import Client, TestCase
from django.urls import reverse

from .models import Partida


class ViewsTest(TestCase):

    def criar_partida(self, dificuldade="facil"):
        return self.client.post(
            reverse("criar_partida"),
            data=json.dumps({"dificuldade": dificuldade}),
            content_type="application/json",
        )

    def test_pagina_inicial_abre(self):
        resposta = self.client.get(reverse("lobby"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Jogo da Memória")

    def test_criar_partida(self):
        resposta = self.criar_partida()

        self.assertEqual(resposta.status_code, 201)

        dados = resposta.json()
        self.assertEqual(
            dados["mensagem"],
            "Partida criada com sucesso.",
        )
        self.assertEqual(
            dados["partida"]["dificuldade"],
            "facil",
        )

        self.assertTrue(
            Partida.objects.filter(
                pk=dados["partida"]["id"]
            ).exists()
        )

    def test_dificuldade_invalida_usa_medio(self):
        resposta = self.criar_partida("impossivel")

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(
            resposta.json()["partida"]["dificuldade"],
            "medio",
        )

    def test_criar_partida_com_json_invalido(self):
        resposta = self.client.post(
            reverse("criar_partida"),
            data="{json inválido",
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)

    def test_estado_da_partida(self):
        resposta_criacao = self.criar_partida()
        partida_id = resposta_criacao.json()["partida"]["id"]

        resposta = self.client.get(
            reverse(
                "estado_partida",
                kwargs={"partida_id": partida_id},
            )
        )

        self.assertEqual(resposta.status_code, 200)

        partida = resposta.json()["partida"]
        self.assertEqual(partida["id"], partida_id)
        self.assertEqual(len(partida["cartas"]), 24)
        self.assertEqual(partida["status"], "jogando")

        # As cartas ainda escondidas não podem ser reveladas.
        self.assertTrue(
            all(carta is None for carta in partida["cartas"])
        )

    def test_virar_primeira_carta(self):
        resposta_criacao = self.criar_partida()
        partida_id = resposta_criacao.json()["partida"]["id"]

        resposta = self.client.post(
            reverse(
                "virar_carta",
                kwargs={"partida_id": partida_id},
            ),
            data=json.dumps({"posicao": 0}),
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)

        dados = resposta.json()
        self.assertTrue(
            any(
                evento["tipo"] == "virar"
                for evento in dados["eventos"]
            )
        )
        self.assertIsNotNone(
            dados["partida"]["cartas"][0]
        )

    def test_virar_carta_com_posicao_invalida(self):
        resposta_criacao = self.criar_partida()
        partida_id = resposta_criacao.json()["partida"]["id"]

        resposta = self.client.post(
            reverse(
                "virar_carta",
                kwargs={"partida_id": partida_id},
            ),
            data=json.dumps({"posicao": 99}),
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.json())

    def test_nao_acessar_partida_de_outra_sessao(self):
        resposta_criacao = self.criar_partida()
        partida_id = resposta_criacao.json()["partida"]["id"]

        # Um cliente diferente representa outro navegador.
        outro_cliente = Client()

        resposta = outro_cliente.get(
            reverse(
                "estado_partida",
                kwargs={"partida_id": partida_id},
            )
        )

        self.assertEqual(resposta.status_code, 404)

    def test_criar_partida_nao_aceita_get(self):
        resposta = self.client.get(reverse("criar_partida"))

        self.assertEqual(resposta.status_code, 405)
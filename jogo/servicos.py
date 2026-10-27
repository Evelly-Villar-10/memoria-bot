from django.db import transaction
from django.db.models import Count, Min, Q

from .bot import turno_bot
from .models import Partida
from .regras import (
    Carta, formam_par, novo_estado, posicoes_livres, resolver_par, resultado,
)


class ErroJogo(Exception):
    """Jogada inválida (carta que não existe, partida acabada etc.)."""


def criar_partida(sessao, dificuldade):
    if dificuldade not in ("facil", "medio", "dificil"):
        dificuldade = "medio"
    return Partida.objects.create(
        sessao=sessao, dificuldade=dificuldade, estado=novo_estado()
    )


@transaction.atomic
def virar_carta(sessao, partida_id, pos):
    partida = Partida.objects.select_for_update().get(pk=partida_id, sessao=sessao)
    estado = partida.estado

    # Validar (o servidor confere tudo, sem confiar no navegador)
    if partida.status != "jogando":
        raise ErroJogo("A partida já terminou.")
    if not isinstance(pos, int) or not 0 <= pos < len(estado["cartas"]):
        raise ErroJogo("Posição inválida.")
    if estado["dono"][pos] is not None:
        raise ErroJogo("Essa carta já formou um par.")
    if pos in estado["viradas"]:
        raise ErroJogo("Você já virou essa carta.")

    # Virar a carta
    eventos = []
    codigo = estado["cartas"][pos]
    estado["viradas"].append(pos)
    estado["memoria_bot"][str(pos)] = codigo
    eventos.append({"tipo": "virar", "pos": pos, "carta": codigo, "quem": "jogador"})

    # Se foi a segunda carta, conferir o par
    if len(estado["viradas"]) == 2:
        a, b = estado["viradas"]
        estado["viradas"] = []
        estado["jogadas"] += 1

        carta_a = Carta.de_codigo(estado["cartas"][a])
        carta_b = Carta.de_codigo(estado["cartas"][b])

        if formam_par(carta_a, carta_b):
            resolver_par(estado, a, b, "jogador")
            eventos.append({"tipo": "par", "pos": [a, b], "dono": "jogador"})
        else:
            eventos.append({"tipo": "erro", "pos": [a, b]})
            eventos += turno_bot(estado, partida.dificuldade)

    # Ver se acabou
    if not posicoes_livres(estado):
        partida.status = "fim"
        partida.resultado = resultado(estado)
        eventos.append({"tipo": "fim", "resultado": partida.resultado,
                        "placar": estado["placar"]})

    # Salvar (placar e jogadas vão também para as colunas, para o histórico)
    partida.pares_jogador = estado["placar"]["jogador"]
    partida.pares_bot = estado["placar"]["bot"]
    partida.jogadas = estado["jogadas"]
    partida.estado = estado
    partida.save()
    return eventos


def historico(sessao, limite=10):
    """Últimas partidas terminadas deste navegador."""
    return Partida.objects.filter(sessao=sessao, status="fim").order_by("-criada_em")[:limite]


def estatisticas(sessao):
    """Totais de vitórias, derrotas, empates e o melhor jogo."""
    return Partida.objects.filter(sessao=sessao, status="fim").aggregate(
        total=Count("id"),
        vitorias=Count("id", filter=Q(resultado="vitoria")),
        derrotas=Count("id", filter=Q(resultado="derrota")),
        empates=Count("id", filter=Q(resultado="empate")),
        melhor=Min("jogadas", filter=Q(resultado="vitoria")),
    )
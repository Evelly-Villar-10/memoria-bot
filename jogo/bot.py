import random

from .regras import Carta, formam_par, posicoes_livres, resolver_par

# Chance de o bot esquecer cada carta que viu no começo da vez dele
ESQUECIMENTO = {"facil": 0.60, "medio": 0.35, "dificil": 0.10}


def _virar(estado, pos, eventos):
    """Vira uma carta: o bot memoriza e registra o evento"""
    codigo = estado["cartas"][pos]
    estado["memoria_bot"][str(pos)] = codigo
    eventos.append({"tipo": "virar", "pos": pos, "carta": codigo, "quem": "bot"})
    return Carta.de_codigo(codigo)


def _par_conhecido(memoria):
    """Procura entre as cartas que o bot lembra duas que formam par"""
    itens = [(int(pos), Carta.de_codigo(cod)) for pos, cod in memoria.items()]
    for i, (pos1, carta1) in enumerate(itens):
        for pos2, carta2 in itens[i + 1:]:
            if formam_par(carta1, carta2):
                return pos1, pos2
    return None


def turno_bot(estado, dificuldade, esquecimento=None):
    """Joga a vez do bot até ele errar ou as cartas acabarem
    Devolve a lista de eventos do que aconteceu"""
    taxa = ESQUECIMENTO[dificuldade] if esquecimento is None else esquecimento
    eventos = []
    memoria = estado["memoria_bot"]

    # 1. esquece algumas cartas
    for pos in list(memoria):
        if random.random() < taxa:
            del memoria[pos]

    while posicoes_livres(estado):
        conhecido = _par_conhecido(memoria)

        if conhecido:
            # 2. joga o par que ele lembra
            a, b = conhecido
            carta_a = _virar(estado, a, eventos)
            carta_b = _virar(estado, b, eventos)
        else:
            # 3. vira uma carta que nunca viu
            livres = posicoes_livres(estado)
            desconhecidas = [p for p in livres if str(p) not in memoria]
            a = random.choice(desconhecidas)
            carta_a = _virar(estado, a, eventos)

            # procura a parceira entre as cartas que lembra
            b = None
            for pos, cod in memoria.items():
                if int(pos) != a and formam_par(carta_a, Carta.de_codigo(cod)):
                    b = int(pos)
                    break

            # 4. senão, vira outra carta desconhecida
            if b is None:
                restantes = [p for p in desconhecidas if p != a]
                b = random.choice(restantes or [p for p in livres if p != a])
            carta_b = _virar(estado, b, eventos)

        if formam_par(carta_a, carta_b):
            resolver_par(estado, a, b, "bot")
            eventos.append({"tipo": "par", "pos": [a, b], "dono": "bot"})
        else:
            eventos.append({"tipo": "erro", "pos": [a, b]})
            break

    return eventos
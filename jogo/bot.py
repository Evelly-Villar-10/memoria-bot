
import random

from .regras import Carta, formam_par, posicoes_livres, resolver_par


# Chance de esquecer cada carta entre as jogadas do bot.
# Quanto maior o valor, mais fácil fica para o jogador.
ESQUECIMENTO = {
    "facil": 0.70,
    "medio": 0.35,
    "dificil": 0.10,
}


def _esquecer(memoria, taxa):
    """Esquece aleatoriamente algumas cartas conhecidas."""
    for pos in list(memoria):
        if random.random() < taxa:
            del memoria[pos]


def _virar(estado, pos, eventos):
    """Vira uma carta e registra o que o bot viu."""
    codigo = estado["cartas"][pos]

    estado["memoria_bot"][str(pos)] = codigo

    eventos.append({
        "tipo": "virar",
        "pos": pos,
        "carta": codigo,
        "quem": "bot",
    })

    return Carta.de_codigo(codigo)


def _par_conhecido(memoria, livres):
    """Procura um par lembrado entre as cartas ainda disponíveis."""
    cartas_conhecidas = [
        (int(pos), Carta.de_codigo(codigo))
        for pos, codigo in memoria.items()
        if int(pos) in livres
    ]

    for i, (pos1, carta1) in enumerate(cartas_conhecidas):
        for pos2, carta2 in cartas_conhecidas[i + 1:]:
            if formam_par(carta1, carta2):
                return pos1, pos2

    return None


def turno_bot(estado, dificuldade, esquecimento=None):
    """
    O bot joga até errar ou acabarem as cartas.
    Esquece informações entre as tentativas de formar pares.
    """
    taxa = (
        ESQUECIMENTO[dificuldade]
        if esquecimento is None
        else esquecimento
    )

    taxa = max(0.0, min(1.0, taxa))

    eventos = []
    memoria = estado["memoria_bot"]

    while posicoes_livres(estado):
        livres = set(posicoes_livres(estado))

        # Remove da memória as cartas que já formaram pares.
        for pos in list(memoria):
            if int(pos) not in livres:
                del memoria[pos]

        # O esquecimento acontece antes de cada nova tentativa.
        _esquecer(memoria, taxa)

        livres = set(posicoes_livres(estado))

        # Primeiro, tenta encontrar um par que ainda lembra.
        conhecido = _par_conhecido(memoria, livres)

        if conhecido:
            a, b = conhecido
            carta_a = _virar(estado, a, eventos)
            carta_b = _virar(estado, b, eventos)

        else:
            # Escolhe uma carta livre que ainda não conhece,
            # se houver alguma.
            desconhecidas = [
                pos for pos in livres
                if str(pos) not in memoria
            ]

            a = random.choice(
                desconhecidas if desconhecidas
                else list(livres)
            )

            carta_a = _virar(estado, a, eventos)

            # Verifica se conhece a parceira da primeira carta.
            b = None

            for pos, codigo in memoria.items():
                pos = int(pos)

                if (
                    pos != a
                    and pos in livres
                    and formam_par(
                        carta_a,
                        Carta.de_codigo(codigo)
                    )
                ):
                    b = pos
                    break

            # Se não conhece a parceira, escolhe outra carta livre.
            if b is None:
                restantes = list(livres - {a})
                b = random.choice(restantes)

            carta_b = _virar(estado, b, eventos)

        if formam_par(carta_a, carta_b):
            resolver_par(estado, a, b, "bot")

            eventos.append({
                "tipo": "par",
                "pos": [a, b],
                "dono": "bot",
            })

            # A próxima tentativa terá uma nova chance de esquecer.
            # O bot não perde automaticamente os pares que já acertou.
        else:
            eventos.append({
                "tipo": "erro",
                "pos": [a, b],
            })
            break

    return eventos

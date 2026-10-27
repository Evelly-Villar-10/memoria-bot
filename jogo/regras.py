import random
from dataclasses import dataclass

TOTAL_PARES = 12


@dataclass(frozen=True)
class Carta:
    valor: int   # 1=Ás, 2 a 10, 11=Valete, 12=Dama, 13=Rei
    naipe: str   # S=espadas, H=copas, D=ouros, C=paus

    @property
    def codigo(self):
        return f"{self.valor}{self.naipe}"

    @staticmethod
    def de_codigo(texto):
        return Carta(int(texto[:-1]), texto[-1])


def cor(carta):
    return "V" if carta.naipe in "HD" else "P"


def formam_par(a, b):
    """Par = mesmo valor e mesma cor (7 de copas com 7 de ouros)."""
    return a != b and a.valor == b.valor and cor(a) == cor(b)


def criar_tabuleiro(pares=TOTAL_PARES):
    """Sorteia 12 valores, cada um vira duas cartas da mesma cor."""
    cartas = []
    for valor in random.sample(range(1, 14), pares):
        naipes = random.choice(["HD", "SC"])   # as duas vermelhas ou as duas pretas
        cartas.append(Carta(valor, naipes[0]))
        cartas.append(Carta(valor, naipes[1]))
    random.shuffle(cartas)
    return cartas


def novo_estado():
    cartas = criar_tabuleiro()
    return {
        "cartas": [c.codigo for c in cartas],
        "dono": [None] * len(cartas),    # None, "jogador" ou "bot" (par já formado)
        "viradas": [],                   # cartas viradas agora, na vez do jogador
        "memoria_bot": {},               # o que o bot lembra: {"posição": "código"}
        "placar": {"jogador": 0, "bot": 0},
        "jogadas": 0,
    }


def posicoes_livres(estado):
    return [i for i, d in enumerate(estado["dono"]) if d is None]


def resolver_par(estado, a, b, quem):
    estado["dono"][a] = estado["dono"][b] = quem
    estado["placar"][quem] += 1
    estado["memoria_bot"].pop(str(a), None)
    estado["memoria_bot"].pop(str(b), None)


def resultado(estado):
    j = estado["placar"]["jogador"]
    b = estado["placar"]["bot"]
    if j > b:
        return "vitoria"
    if b > j:
        return "derrota"
    return "empate"
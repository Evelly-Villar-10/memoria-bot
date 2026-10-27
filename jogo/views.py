import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Partida
from .servicos import (
    ErroJogo,
    criar_partida,
    estatisticas,
    historico,
    virar_carta,
)

@ensure_csrf_cookie
def lobby(request):
    sessao = obter_sessao(request)
    return render(request, "jogo/lobby.html", {
        "estatisticas": estatisticas(sessao),
        "historico": historico(sessao),
    })


def obter_dados(request):
    """Lê os dados enviados pelo navegador."""
    if request.content_type == "application/json":
        try:
            return json.loads(request.body or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    return request.POST


def obter_sessao(request):
    """Garante que este navegador tenha uma sessão."""
    if request.session.session_key is None:
        request.session.create()

    return request.session.session_key


def estado_publico(partida):
    """
    Devolve o estado do jogo sem revelar as cartas escondidas.
    """
    estado = partida.estado
    cartas_visiveis = []

    for pos, codigo in enumerate(estado["cartas"]):
        if (
            estado["dono"][pos] is not None
            or pos in estado["viradas"]
        ):
            cartas_visiveis.append(codigo)
        else:
            cartas_visiveis.append(None)

    return {
        "id": partida.pk,
        "dificuldade": partida.dificuldade,
        "status": partida.status,
        "resultado": partida.resultado,
        "cartas": cartas_visiveis,
        "dono": estado["dono"],
        "viradas": estado["viradas"],
        "placar": estado["placar"],
        "jogadas": estado["jogadas"],
    }


@require_POST
def criar_partida_view(request):
    dados = obter_dados(request)

    if dados is None:
        return JsonResponse(
            {"erro": "O corpo da requisição não contém JSON válido."},
            status=400,
        )

    dificuldade = dados.get("dificuldade", "medio")

    sessao = obter_sessao(request)
    partida = criar_partida(sessao, dificuldade)

    return JsonResponse(
        {
            "mensagem": "Partida criada com sucesso.",
            "partida": estado_publico(partida),
        },
        status=201,
    )


@require_POST
def virar_carta_view(request, partida_id):
    dados = obter_dados(request)

    if dados is None:
        return JsonResponse(
            {"erro": "O corpo da requisição não contém JSON válido."},
            status=400,
        )

    try:
        posicao = int(dados.get("posicao"))
    except (TypeError, ValueError):
        return JsonResponse(
            {"erro": "Informe uma posição válida."},
            status=400,
        )

    sessao = obter_sessao(request)

    try:
        eventos = virar_carta(sessao, partida_id, posicao)

        partida = Partida.objects.get(
            pk=partida_id,
            sessao=sessao,
        )

    except Partida.DoesNotExist:
        return JsonResponse(
            {"erro": "Partida não encontrada."},
            status=404,
        )

    except ErroJogo as erro:
        return JsonResponse(
            {"erro": str(erro)},
            status=400,
        )

    return JsonResponse(
        {
            "eventos": eventos,
            "partida": estado_publico(partida),
        }
    )


@require_GET
def estado_partida_view(request, partida_id):
    sessao = request.session.session_key

    if sessao is None:
        return JsonResponse(
            {"erro": "Partida não encontrada."},
            status=404,
        )

    try:
        partida = Partida.objects.get(
            pk=partida_id,
            sessao=sessao,
        )
    except Partida.DoesNotExist:
        return JsonResponse(
            {"erro": "Partida não encontrada."},
            status=404,
        )

    return JsonResponse(
        {"partida": estado_publico(partida)}
    )
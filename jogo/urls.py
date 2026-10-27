from django.urls import path

from . import views


urlpatterns = [
    path("", views.lobby, name="lobby"),

    path(
        "api/partidas/",
        views.criar_partida_view,
        name="criar_partida",
    ),

    path(
        "api/partidas/<int:partida_id>/virar/",
        views.virar_carta_view,
        name="virar_carta",
    ),

    path(
        "api/partidas/<int:partida_id>/estado/",
        views.estado_partida_view,
        name="estado_partida",
    ),
]
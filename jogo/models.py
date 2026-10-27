from django.db import models


class Partida(models.Model):
    sessao = models.CharField(max_length=40, db_index=True)
    dificuldade = models.CharField(max_length=10, default="medio")
    estado = models.JSONField(default=dict)
    status = models.CharField(max_length=10, default="jogando")
    resultado = models.CharField(max_length=10, blank=True)
    pares_jogador = models.PositiveSmallIntegerField(default=0)
    pares_bot = models.PositiveSmallIntegerField(default=0)
    jogadas = models.PositiveSmallIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Partida {self.pk} ({self.dificuldade}, {self.status})"
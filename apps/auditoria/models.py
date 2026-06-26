"""
Modelo LogAuditoria
apps/auditoria/models.py
"""
from django.db import models
from apps.usuarios.models import Usuario

class LogAuditoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    tabla_afectada = models.CharField(max_length=50, blank=True)
    id_registro_afectado = models.IntegerField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    datos_previos = models.TextField(blank=True)
    datos_nuevos = models.TextField(blank=True)
    ip_origen = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.accion} por {self.usuario} el {self.fecha_hora}"
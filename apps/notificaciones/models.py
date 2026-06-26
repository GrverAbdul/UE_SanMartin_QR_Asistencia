"""
Modelo Notificacion
apps/notificaciones/models.py
"""
from django.db import models
from apps.usuarios.models import Usuario

class Notificacion(models.Model):
    TIPO_NOTIFICACION = [
        ('inasistencia', 'Inasistencia'),
        ('permiso', 'Permiso'),
        ('sistema', 'Sistema'),
    ]
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    tipo_notificacion = models.CharField(max_length=20, choices=TIPO_NOTIFICACION)

    def __str__(self):
        return f"{self.titulo} - {self.destinatario.username}"
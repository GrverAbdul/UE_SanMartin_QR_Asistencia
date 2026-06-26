"""
Modelo Permiso
apps/permisos/models.py
"""
from django.db import models
from apps.usuarios.models import Usuario

class Permiso(models.Model):
    TIPO_PERMISO = [
        ('estudio', 'Estudio'),
        ('salud', 'Salud'),
        ('personal', 'Personal'),
        ('otro', 'Otro'),
    ]
    ESTADO_PERMISO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='permisos_solicitados')
    autorizador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='permisos_autorizados')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.TextField()
    tipo_permiso = models.CharField(max_length=20, choices=TIPO_PERMISO)
    estado_permiso = models.CharField(max_length=20, choices=ESTADO_PERMISO, default='pendiente')
    archivo_justificacion = models.FileField(upload_to='justificaciones/', null=True, blank=True)

    def __str__(self):
        return f"Permiso {self.solicitante.username} ({self.estado_permiso})"
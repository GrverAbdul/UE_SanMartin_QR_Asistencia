"""
Modelo Asistencia.
apps/asistencia/models.py
"""
from django.db import models
from django.utils import timezone
from apps.usuarios.models import Usuario, Estudiante, Docente, Administrativo

class Asistencia(models.Model):
    TIPO_USUARIO = [
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
    ]
    ESTADO_ASISTENCIA = [
        ('presente', 'Presente'),
        ('tarde', 'Tarde'),
        ('ausente', 'Ausente'),
        ('justificado', 'Justificado'),
    ]
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asistencias_registradas')
    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, null=True, blank=True)
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, null=True, blank=True)
    administrativo = models.ForeignKey(Administrativo, on_delete=models.CASCADE, null=True, blank=True)
    estado_asistencia = models.CharField(max_length=20, choices=ESTADO_ASISTENCIA, default='presente')
    observacion = models.TextField(blank=True)

    def __str__(self):
        persona = self.estudiante or self.docente or self.administrativo
        return f"Asistencia {self.tipo_usuario} - {persona} [{self.estado_asistencia}]"
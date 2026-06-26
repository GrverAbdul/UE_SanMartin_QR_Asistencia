"""
Señal para registrar automáticamente cambios en modelos importantes.
apps/auditoria/signals.py
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.asistencia.models import Asistencia
from apps.permisos.models import Permiso
from apps.usuarios.models import Usuario
from .models import LogAuditoria
import json

def log_cambio(sender, instance, created, **kwargs):
    if created:
        accion = 'creación'
    else:
        accion = 'actualización'
    LogAuditoria.objects.create(
        usuario=instance.usuario_registro if hasattr(instance, 'usuario_registro') else None,
        accion=accion,
        tabla_afectada=sender._meta.model_name,
        id_registro_afectado=instance.pk,
        datos_nuevos=json.dumps(instance.__dict__, default=str)
    )

post_save.connect(log_cambio, sender=Asistencia)
post_save.connect(log_cambio, sender=Permiso)
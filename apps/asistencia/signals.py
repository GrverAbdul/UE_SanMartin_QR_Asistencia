# apps/asistencia/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import Asistencia
from apps.usuarios.models import PadreEstudiante
from apps.notificaciones.models import Notificacion

@receiver(post_save, sender=Asistencia)
def notificar_faltas_criticas(sender, instance, created, **kwargs):
    # Solo al crear una nueva asistencia de tipo 'ausente' o 'tarde' para estudiante
    if not created or instance.tipo_usuario != 'estudiante':
        return
    if instance.estado_asistencia not in ['ausente', 'tarde']:
        return

    estudiante = instance.estudiante
    limite = settings.FALTAS_NOTIFICACION
    inicio_mes = timezone.now().date().replace(day=1)

    # Contar faltas injustificadas en el mes actual
    faltas = Asistencia.objects.filter(
        estudiante=estudiante,
        fecha_hora__date__gte=inicio_mes,
        estado_asistencia__in=['ausente', 'tarde']
    ).count()

    if faltas > limite:
        # Evitar notificar si ya se envió una notificación no leída por el mismo motivo este mes
        ya_notificado = Notificacion.objects.filter(
            destinatario__in=[p.padre for p in PadreEstudiante.objects.filter(estudiante=estudiante)],
            tipo_notificacion='inasistencia',
            leido=False,
            mensaje__icontains=f"más de {limite} faltas"
        ).exists()
        if not ya_notificado:
            for relacion in PadreEstudiante.objects.filter(estudiante=estudiante):
                Notificacion.objects.create(
                    destinatario=relacion.padre,
                    titulo="Alerta de inasistencia",
                    mensaje=f"Su hijo {estudiante.usuario.get_full_name()} ha acumulado más de {limite} faltas en el mes.",
                    tipo_notificacion='inasistencia'
                )
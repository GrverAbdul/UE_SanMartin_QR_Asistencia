#Señales para el model de usuarios
# apps/usuarios/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Estudiante, Docente, Administrativo

@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Solo crea perfil automático si el usuario no es superusuario
        if instance.rol == 'estudiante' and not hasattr(instance, 'estudiante'):
            Estudiante.objects.create(usuario=instance, codigo_estudiante=f"TEMP-{instance.pk}")
        elif instance.rol == 'docente' and not hasattr(instance, 'docente'):
            Docente.objects.create(usuario=instance)
        elif instance.rol == 'administrativo' and not hasattr(instance, 'administrativo'):
            Administrativo.objects.create(usuario=instance)
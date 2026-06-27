#Modelos de usuario y perfiles.
# apps/usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('administrativo', 'Administrativo'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
        ('directivo', 'Directivo'),
        ('padre', 'Padre de familia'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante')
    email = models.EmailField(unique=True, null=True, blank=True, default=None)

    # Datos personales (antes en Persona)
    ci = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Cédula de Identidad')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

    qr_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    debe_cambiar_contrasena = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    #para cambiar de rol 
    def save(self, *args, **kwargs):
        # Si el usuario ya existe (tiene pk) y el rol ha cambiado, eliminar el perfil antiguo
        if self.pk:
            try:
                old = Usuario.objects.get(pk=self.pk)
                if old.rol != self.rol:
                    # Eliminar el perfil del rol anterior
                    if old.rol == 'estudiante' and hasattr(old, 'estudiante'):
                        old.estudiante.delete()
                    elif old.rol == 'docente' and hasattr(old, 'docente'):
                        old.docente.delete()
                    elif old.rol == 'administrativo' and hasattr(old, 'administrativo'):
                        old.administrativo.delete()
                    # Crear el nuevo perfil (si corresponde)
                    if self.rol == 'estudiante' and not hasattr(self, 'estudiante'):
                        Estudiante.objects.create(usuario=self, codigo_estudiante=f"TEMP-{self.pk}")
                    elif self.rol == 'docente' and not hasattr(self, 'docente'):
                        Docente.objects.create(usuario=self)
                    elif self.rol == 'administrativo' and not hasattr(self, 'administrativo'):
                        Administrativo.objects.create(usuario=self)
            except Usuario.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante')
    codigo_estudiante = models.CharField(max_length=20, unique=True)
    curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True, related_name='estudiantes')

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.codigo_estudiante}"


class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='docente')
    profesionalidad = models.CharField(max_length=100, blank=True)
    especialidad = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Docente: {self.usuario.get_full_name()}"


class Administrativo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='administrativo')
    cargo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Admin: {self.usuario.get_full_name()}"


class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    NIVEL_CHOICES = [
        ('1ro Sec', 'Primero de Secundaria'),
        ('2do Sec', 'Segundo de Secundaria'),
        ('3ro Sec', 'Tercero de Secundaria'),
        ('4to Sec', 'Cuarto de Secundaria'),
        ('5to Sec', 'Quinto de Secundaria'),
        ('6to Sec', 'Sexto de Secundaria'),
    ]
    PARALELO_CHOICES = [
        ('A', 'Paralelo A'),
        ('B', 'Paralelo B'),
        ('C', 'Paralelo C'),
    ]
    nombre = models.CharField(max_length=10, choices=NIVEL_CHOICES)
    paralelo = models.CharField(max_length=1, choices=PARALELO_CHOICES)
    turno = models.CharField(max_length=20, blank=True)
    docente_tutor = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos_tutorados')
    materias = models.ManyToManyField(Materia, related_name='cursos', blank=True)

    class Meta:
        unique_together = ('nombre', 'paralelo')

    def __str__(self):
        return f"{self.get_nombre_display()} - {self.get_paralelo_display()}"

# apps/usuarios/models.py (añadir al final)
class PadreEstudiante(models.Model):
    """Relación entre un padre de familia y sus hijos estudiantes."""
    padre = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='hijos_relacion', limit_choices_to={'rol': 'padre'})
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='padres_relacion')

    class Meta:
        verbose_name = "Asignación Padre-Estudiante"
        verbose_name_plural = "Asignaciones Padre-Estudiante"
        unique_together = ('padre', 'estudiante')

    def __str__(self):
        return f"{self.padre.get_full_name()} → {self.estudiante.usuario.get_full_name()}"
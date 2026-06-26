#apps/usuarios/management/commands/cargar_materia.py
from django.core.management.base import BaseCommand
from apps.usuarios.models import Materia

class Command(BaseCommand):
    help = 'Las materias del currículo boliviano de secundaria'

    def handle(self, *args, **options):
        materias = [
            'Matemáticas', 'Lenguaje y Literatura', 'Ciencias Sociales',
            'Física', 'Química', 'Biología', 'Geografía', 'Historia',
            'Filosofía', 'Inglés', 'Educación Física', 'Artes Plásticas',
            'Ciencias Naturales', 'Música', 'Computación', 'Religión', 'Valores',
            'Oeiwntación Vocacional', 'Técnica Vocacional',
        ]
        for nombre in materias:
            Materia.objects.get_or_create(nombre=nombre)
        self.stdout.write(self.style.SUCCESS('Materias cargadas exitosamente.'))
import os
import random
import string
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asistencia_qr.settings')
import django
django.setup()

from apps.usuarios.models import Usuario, Estudiante, Curso

# Cursos disponibles (paralelo A)
niveles = ['1ro Sec', '2do Sec', '3ro Sec', '4to Sec', '5to Sec', '6to Sec']
cursos_a = []
for n in niveles:
    try:
        curso = Curso.objects.get(nombre=n, paralelo='A')
        cursos_a.append(curso)
    except Curso.DoesNotExist:
        print(f'⚠️ Falta curso: {n} A')

if not cursos_a:
    print('No hay cursos A creados. Aborta.')
    exit()

# Generador de cadena aleatoria para email
def random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Crear 50 estudiantes
for i in range(10, 60):
    username = f'estudiante{i}'
    if Usuario.objects.filter(username=username).exists():
        print(f'⚠️ {username} ya existe, se omite.')
        continue

    # Email único aleatorio
    email = f'{username}_{random_string(4)}@uesanmartin.com'

    # Datos personales variados
    ci = str(1000000 + random.randint(0, 999999))  # CI entre 1000000 y 1999999
    first_name = f'Estudiante{i}'
    last_name = random.choice(['Lilo', 'Stich', 'Pérez', 'García', 'Mamani', 'Quispe', 'Condori', 'Flores', 'López'])
    telefono = str(70000000 + random.randint(0, 9999999))  # teléfono de 8 dígitos
    direccion = f'Calle {random.choice(["A","B","C"])}, # {random.randint(1,999)}'
    # Fecha de nacimiento aleatoria entre 2006 y 2014 (edad aprox. 12-20)
    ano = random.randint(2006, 2014)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)  # para evitar problemas con meses
    fecha_nac = date(ano, mes, dia)

    user = Usuario.objects.create_user(
        username=username,
        password=username,        # contraseña igual al username
        first_name=first_name,
        last_name=last_name,
        email=email,
        rol='estudiante',
        ci=ci,
        telefono=telefono,
        direccion=direccion,
        fecha_nacimiento=fecha_nac,
    )

    # Asignar curso rotativo
    curso_asignado = cursos_a[(i - 10) % len(cursos_a)]
    estudiante = Estudiante.objects.get(usuario=user)
    estudiante.curso = curso_asignado
    estudiante.save()

    print(f'✅ {username} | Email: {email} | Curso: {curso_asignado.nombre} {curso_asignado.paralelo}')

print('Proceso finalizado. 50 estudiantes creados.')
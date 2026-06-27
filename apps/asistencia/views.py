#Vistas para registro de asistencia (QR y manual), historial.
# apps/asistencia/views.py
import json
from datetime import date, datetime, time as dtime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.usuarios.models import Usuario, Estudiante, Docente, Administrativo, Curso, PadreEstudiante
from apps.usuarios.decorators import role_required
from .models import Asistencia

@login_required
@role_required('administrativo')           # solo administrativos
def escaner_view(request):
    return render(request, 'asistencia/escaner.html')

@login_required
@role_required('administrativo')
def registrar_asistencia_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
        qr_id = data.get('qr_id')
        if not qr_id:
            return JsonResponse({'success': False, 'error': 'QR no proporcionado'}, status=400)
        try:
            usuario = Usuario.objects.get(qr_code=qr_id)
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'QR no válido'}, status=404)

        # Obtener la hora actual en la zona horaria de Bolivia
        ahora_utc = timezone.now()
        ahora_local = timezone.localtime(ahora_utc)          # hora local de La Paz
        hoy_local = ahora_local.date()

        # Hora límite en Bolivia (8:00 AM)
        hora_limite = dtime(8, 0)
        estado = 'presente' if ahora_local.time() <= hora_limite else 'tarde'

        tipo = usuario.rol

        # Verificar si ya registró asistencia en el día local
        # Para evitar problemas con la diferencia de huso, delimitamos el rango UTC del día local
        inicio_dia_local = timezone.make_aware(
            datetime.combine(hoy_local, dtime.min), timezone.get_current_timezone()
        )
        fin_dia_local = inicio_dia_local + timedelta(days=1)

        if tipo == 'estudiante':
            try:
                estudiante = Estudiante.objects.get(usuario=usuario)
            except Estudiante.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Perfil estudiante no encontrado'}, status=404)

            existe = Asistencia.objects.filter(
                tipo_usuario='estudiante',
                estudiante=estudiante,
                fecha_hora__gte=inicio_dia_local,
                fecha_hora__lt=fin_dia_local
            ).exists()
            if existe:
                return JsonResponse({'success': False, 'error': 'Ya registró asistencia hoy'}, status=409)

            Asistencia.objects.create(
                usuario_registro=request.user,
                fecha_hora=ahora_utc,          # se guarda en UTC
                tipo_usuario='estudiante',
                estudiante=estudiante,
                estado_asistencia=estado
            )
        elif tipo == 'docente':
            try:
                docente = Docente.objects.get(usuario=usuario)
            except Docente.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Perfil docente no encontrado'}, status=404)

            existe = Asistencia.objects.filter(
                tipo_usuario='docente',
                docente=docente,
                fecha_hora__gte=inicio_dia_local,
                fecha_hora__lt=fin_dia_local
            ).exists()
            if existe:
                return JsonResponse({'success': False, 'error': 'Ya registró asistencia hoy'}, status=409)

            Asistencia.objects.create(
                usuario_registro=request.user,
                fecha_hora=ahora_utc,
                tipo_usuario='docente',
                docente=docente,
                estado_asistencia=estado
            )
        elif tipo == 'administrativo':
            try:
                administrativo = Administrativo.objects.get(usuario=usuario)
            except Administrativo.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Perfil administrativo no encontrado'}, status=404)

            existe = Asistencia.objects.filter(
                tipo_usuario='administrativo',
                administrativo=administrativo,
                fecha_hora__gte=inicio_dia_local,
                fecha_hora__lt=fin_dia_local
            ).exists()
            if existe:
                return JsonResponse({'success': False, 'error': 'Ya registró asistencia hoy'}, status=409)

            Asistencia.objects.create(
                usuario_registro=request.user,
                fecha_hora=ahora_utc,
                tipo_usuario='administrativo',
                administrativo=administrativo,
                estado_asistencia=estado
            )
        else:
            return JsonResponse({'success': False, 'error': 'Rol no válido'}, status=400)

        return JsonResponse({'success': True, 'nombre': usuario.get_full_name(), 'estado': estado})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
@role_required('docente')
def registro_manual(request):
    docente = Docente.objects.get(usuario=request.user)
    cursos = Curso.objects.filter(docente_tutor=docente)
    estudiantes = []
    curso_seleccionado = None

    # Si se envió un curso por GET o POST, obtenerlo
    curso_id = request.GET.get('curso') or request.POST.get('curso')
    if curso_id:
        try:
            curso_seleccionado = Curso.objects.get(id=curso_id, docente_tutor=docente)
            estudiantes = Estudiante.objects.filter(curso=curso_seleccionado).order_by('usuario__last_name')
        except Curso.DoesNotExist:
            curso_seleccionado = None

    if request.method == 'POST' and curso_seleccionado:
        # Procesar las asistencias enviadas
        ahora_utc = timezone.now()
        ahora_local = timezone.localtime(ahora_utc)
        hoy_local = ahora_local.date()
        inicio_dia_local = timezone.make_aware(
            datetime.combine(hoy_local, dtime.min), timezone.get_current_timezone()
        )
        fin_dia_local = inicio_dia_local + timedelta(days=1)

        for est in estudiantes:
            estado_key = f'estado_{est.id}'
            estado = request.POST.get(estado_key, 'ausente')
            # Evitar duplicados en el mismo día
            ya_existe = Asistencia.objects.filter(
                tipo_usuario='estudiante',
                estudiante=est,
                fecha_hora__gte=inicio_dia_local,
                fecha_hora__lt=fin_dia_local
            ).exists()
            if not ya_existe and estado != 'ausente':  # solo guardar si no es ausente y no existe registro
                Asistencia.objects.create(
                    usuario_registro=request.user,
                    fecha_hora=ahora_utc,
                    tipo_usuario='estudiante',
                    estudiante=est,
                    estado_asistencia=estado
                )
        messages.success(request, 'Asistencia registrada correctamente.')
        return redirect('registro_manual')

    context = {
        'cursos': cursos,
        'curso_seleccionado': curso_seleccionado,
        'estudiantes': estudiantes,
    }
    return render(request, 'asistencia/manual.html', context)

# apps/asistencia/views.py (reemplaza la función historial)
@login_required
def historial(request):
    user = request.user
    asistencias = []
    hijos = None
    hijo_seleccionado = None

    if user.rol == 'estudiante':
        try:
            estudiante = Estudiante.objects.get(usuario=user)
            asistencias = Asistencia.objects.filter(estudiante=estudiante).order_by('-fecha_hora')
        except Estudiante.DoesNotExist:
            pass

    elif user.rol == 'docente':
        try:
            docente = Docente.objects.get(usuario=user)
            asistencias = Asistencia.objects.filter(docente=docente).order_by('-fecha_hora')
        except Docente.DoesNotExist:
            pass

    elif user.rol == 'administrativo':
        try:
            administrativo = Administrativo.objects.get(usuario=user)
            asistencias = Asistencia.objects.filter(administrativo=administrativo).order_by('-fecha_hora')
        except Administrativo.DoesNotExist:
            pass

    elif user.rol == 'padre':
        # Obtener los hijos del padre
        relaciones = PadreEstudiante.objects.filter(padre=user).select_related('estudiante__usuario', 'estudiante__curso')
        hijos = [rel.estudiante for rel in relaciones]

        # Si se selecciona un hijo específico
        hijo_id = request.GET.get('hijo_id')
        if hijo_id and hijos:
            try:
                hijo_seleccionado = next(h for h in hijos if str(h.id) == hijo_id)
                asistencias = Asistencia.objects.filter(estudiante=hijo_seleccionado).order_by('-fecha_hora')
            except StopIteration:
                pass

    return render(request, 'asistencia/historial.html', {
        'asistencias': asistencias,
        'hijos': hijos,
        'hijo_seleccionado': hijo_seleccionado,
    })
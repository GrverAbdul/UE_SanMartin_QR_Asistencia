# apps/reportes/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, FileResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, date
from apps.usuarios.decorators import role_required
from apps.asistencia.models import Asistencia
from apps.usuarios.models import Curso, Estudiante, Docente, Administrativo
from .utils import generar_pdf, generar_excel


@login_required
@role_required('administrativo', 'directivo', 'docente')
def generador_reportes(request):
    # Si el usuario es docente, mostrar únicamente los cursos donde es tutor
    if request.user.rol == 'docente':
        try:
            docente = Docente.objects.get(usuario=request.user)
            cursos = Curso.objects.filter(docente_tutor=docente)
        except Docente.DoesNotExist:
            cursos = Curso.objects.none()
    else:
        cursos = Curso.objects.all()

    if request.method == 'POST':
        tipo = request.POST.get('tipo_reporte')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        formato = request.POST.get('formato', 'pdf')
        descargar = request.POST.get('descargar', '')

        # Validar fechas
        try:
            if not fecha_inicio or not fecha_fin:
                return HttpResponseBadRequest("Debe proporcionar fecha de inicio y fin.")
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio).date()
            fecha_fin_dt = datetime.fromisoformat(fecha_fin).date()
            if fecha_inicio_dt > fecha_fin_dt:
                return HttpResponseBadRequest("La fecha de inicio no puede ser posterior a la fecha fin.")
        except ValueError:
            return HttpResponseBadRequest("Formato de fecha inválido. Use YYYY-MM-DD.")

        # Bloquear tipos de reporte no permitidos para docentes
        if request.user.rol == 'docente' and tipo not in ['curso', 'estudiante']:
            return HttpResponseBadRequest("Tipo de reporte no autorizado para su rol.")

        asistencias = Asistencia.objects.none()
        datos = []
        columnas = []
        titulo = "Reporte"
        info_extra = {}

        if tipo == 'administrativos':
            asistencias = Asistencia.objects.filter(
                tipo_usuario='administrativo',
                fecha_hora__date__gte=fecha_inicio_dt,
                fecha_hora__date__lte=fecha_fin_dt
            ).select_related('administrativo__usuario')
            datos = [[a.administrativo.usuario.ci or '',
                      a.administrativo.usuario.get_full_name(),
                      a.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                      a.get_estado_asistencia_display()]
                     for a in asistencias]
            columnas = ['CI', 'Nombre', 'Fecha/Hora', 'Estado']
            titulo = "Reporte de Personal Administrativo"

        elif tipo == 'docentes':
            asistencias = Asistencia.objects.filter(
                tipo_usuario='docente',
                fecha_hora__date__gte=fecha_inicio_dt,
                fecha_hora__date__lte=fecha_fin_dt
            ).select_related('docente__usuario')
            datos = [[a.docente.usuario.ci or '',
                      a.docente.usuario.get_full_name(),
                      a.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                      a.get_estado_asistencia_display()]
                     for a in asistencias]
            columnas = ['CI', 'Nombre', 'Fecha/Hora', 'Estado']
            titulo = "Reporte de Personal Docente"

        elif tipo == 'curso':
            curso_id = request.POST.get('curso')
            try:
                curso = Curso.objects.get(id=curso_id)
                if request.user.rol == 'docente':
                    docente = Docente.objects.get(usuario=request.user)
                    if curso.docente_tutor != docente:
                        return HttpResponseBadRequest("No tiene permiso para este curso.")
            except Curso.DoesNotExist:
                return HttpResponseBadRequest("Curso no válido.")

            asistencias = Asistencia.objects.filter(
                tipo_usuario='estudiante',
                estudiante__curso_id=curso_id,
                fecha_hora__date__gte=fecha_inicio_dt,
                fecha_hora__date__lte=fecha_fin_dt
            ).select_related('estudiante__usuario')
            datos = [[a.estudiante.usuario.ci or '',
                      a.estudiante.usuario.get_full_name(),
                      a.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                      a.get_estado_asistencia_display()]
                     for a in asistencias]
            columnas = ['CI', 'Estudiante', 'Fecha/Hora', 'Estado']
            titulo = f"Reporte del Curso {curso.get_nombre_display()} {curso.get_paralelo_display()}"
            info_extra = {'curso': str(curso)}

        elif tipo == 'estudiante':
            estudiante_id = request.POST.get('estudiante')
            try:
                estudiante = Estudiante.objects.select_related('usuario', 'curso').get(id=estudiante_id)
                if request.user.rol == 'docente':
                    docente = Docente.objects.get(usuario=request.user)
                    if estudiante.curso.docente_tutor != docente:
                        return HttpResponseBadRequest("No tiene permiso para este estudiante.")
            except Estudiante.DoesNotExist:
                return HttpResponseBadRequest("Estudiante no válido.")

            asistencias = Asistencia.objects.filter(
                tipo_usuario='estudiante',
                estudiante_id=estudiante_id,
                fecha_hora__date__gte=fecha_inicio_dt,
                fecha_hora__date__lte=fecha_fin_dt
            ).select_related('estudiante__usuario')
            datos = [[a.estudiante.usuario.ci or '',
                      a.estudiante.usuario.get_full_name(),
                      a.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                      a.get_estado_asistencia_display()]
                     for a in asistencias]
            columnas = ['CI', 'Estudiante', 'Fecha/Hora', 'Estado']
            nombre_est = estudiante.usuario.get_full_name()
            titulo = f"Reporte de {nombre_est}"

        # Si se solicita descarga directa
        if descargar == 'pdf':
            buffer = generar_pdf(titulo, datos, columnas)
            return FileResponse(buffer, as_attachment=True, filename='reporte.pdf')
        elif descargar == 'excel':
            buffer = generar_excel(titulo, datos, columnas)
            return FileResponse(buffer, as_attachment=True, filename='reporte.xlsx')

        # Si no se solicita descarga, mostrar vista previa
        context = {
            'cursos': cursos,
            'es_docente': request.user.rol == 'docente',
            'vista_previa': True,
            'datos': datos,
            'columnas': columnas,
            'titulo': titulo,
            'tipo_reporte': tipo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'curso_id': request.POST.get('curso', ''),
            'estudiante_id': request.POST.get('estudiante', ''),
        }
        return render(request, 'reportes/generador.html', context)

    context = {
        'cursos': cursos,
        'es_docente': request.user.rol == 'docente',
    }
    return render(request, 'reportes/generador.html', context)


@login_required
def get_estudiantes_curso(request):
    """Devuelve los estudiantes de un curso en JSON. Solo si el usuario tiene permiso."""
    curso_id = request.GET.get('curso_id')
    if not curso_id:
        return JsonResponse([], safe=False)

    if request.user.rol == 'docente':
        try:
            docente = Docente.objects.get(usuario=request.user)
            if not Curso.objects.filter(id=curso_id, docente_tutor=docente).exists():
                return JsonResponse([], safe=False)
        except Docente.DoesNotExist:
            return JsonResponse([], safe=False)

    estudiantes = Estudiante.objects.filter(curso_id=curso_id).select_related('usuario')
    data = [{'id': e.id, 'nombre': e.usuario.get_full_name()} for e in estudiantes]
    return JsonResponse(data, safe=False)
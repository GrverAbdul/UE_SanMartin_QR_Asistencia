"""
Vistas de permisos.
apps/permisos/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, timedelta, time as dtime

from apps.usuarios.decorators import role_required
from .models import Permiso
from apps.asistencia.models import Asistencia


@login_required
def solicitar_permiso(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        motivo = request.POST.get('motivo')
        tipo_permiso = request.POST.get('tipo_permiso')

        if not all([fecha_inicio, fecha_fin, motivo, tipo_permiso]):
            messages.error(request, 'Faltan campos obligatorios.')
            return redirect('solicitar_permiso')

        permiso = Permiso(
            solicitante=request.user,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            motivo=motivo,
            tipo_permiso=tipo_permiso,
        )
        if 'archivo' in request.FILES:
            permiso.archivo_justificacion = request.FILES['archivo']
        permiso.save()
        messages.success(request, 'Permiso solicitado correctamente.')
        return redirect('lista_permisos')

    return render(request, 'permisos/solicitar.html')


@login_required
def lista_permisos(request):
    user = request.user
    if user.rol in ['administrativo', 'directivo']:
        permisos = Permiso.objects.all()
    else:
        permisos = Permiso.objects.filter(solicitante=user)
    return render(request, 'permisos/lista.html', {'permisos': permisos})


@login_required
@role_required('administrativo', 'directivo')
def aprobar_permiso(request, permiso_id):
    permiso = get_object_or_404(Permiso, pk=permiso_id)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            permiso.estado_permiso = 'aprobado'
            permiso.autorizador = request.user
            permiso.save()

            inicio = permiso.fecha_inicio.date()
            fin = permiso.fecha_fin.date()
            usuario = permiso.solicitante

            # Determinar el perfil específico del usuario
            perfil = None
            tipo = None
            if usuario.rol == 'estudiante':
                try:
                    perfil = usuario.estudiante
                    tipo = 'estudiante'
                except Exception:
                    perfil = None
            elif usuario.rol == 'docente':
                try:
                    perfil = usuario.docente
                    tipo = 'docente'
                except Exception:
                    perfil = None
            elif usuario.rol == 'administrativo':
                try:
                    perfil = usuario.administrativo
                    tipo = 'administrativo'
                except Exception:
                    perfil = None

            if perfil and tipo:
                dia_actual = inicio
                while dia_actual <= fin:
                    # Buscar si ya existe un registro de asistencia para ese día (comparando solo la fecha)
                    asistencia = Asistencia.objects.filter(
                        tipo_usuario=tipo,
                        **{f'{tipo}': perfil},
                        fecha_hora__date=dia_actual
                    ).first()

                    if asistencia:
                        # Actualizar el estado a 'justificado'
                        asistencia.estado_asistencia = 'justificado'
                        asistencia.save()
                    else:
                        # Crear un nuevo registro justificado al mediodía de ese día (hora local)
                        mediodia_local = datetime.combine(dia_actual, dtime(12, 0))
                        mediodia_utc = timezone.make_aware(mediodia_local, timezone.get_current_timezone())
                        Asistencia.objects.create(
                            usuario_registro=request.user,
                            fecha_hora=mediodia_utc,
                            tipo_usuario=tipo,
                            estudiante=perfil if tipo == 'estudiante' else None,
                            docente=perfil if tipo == 'docente' else None,
                            administrativo=perfil if tipo == 'administrativo' else None,
                            estado_asistencia='justificado'
                        )
                    dia_actual += timedelta(days=1)

                messages.success(request, 'Permiso aprobado y asistencias justificadas.')
            else:
                messages.warning(request, 'Permiso aprobado, pero no se encontró perfil del usuario.')
        elif accion == 'rechazar':
            permiso.estado_permiso = 'rechazado'
            permiso.autorizador = request.user
            permiso.save()
            messages.warning(request, 'Permiso rechazado.')

        return redirect('lista_permisos')

    return render(request, 'permisos/aprobar.html', {'permiso': permiso})
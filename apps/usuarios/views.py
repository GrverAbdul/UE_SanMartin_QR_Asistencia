"""
Vistas de autenticación y dashboard.
apps/usuarios/views.py
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.notificaciones.models import Notificacion
from .decorators import role_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView
from django.urls import reverse_lazy
from django.utils import timezone
from apps.asistencia.models import Asistencia
from apps.permisos.models import Permiso
from apps.usuarios.models import PadreEstudiante, Docente, Estudiante, Administrativo, Curso
from django.conf import settings
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Si debe cambiar contraseña, redirigir a cambio de contraseña
            if user.debe_cambiar_contrasena:
                return redirect('password_change')  # nombre de la URL de cambio de pass
            # Redirigir al dashboard según rol
            # ... (código existente)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'usuarios/login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir al dashboard según rol
            if user.rol == 'administrativo':
                return redirect('dashboard_admin')
            elif user.rol == 'docente':
                return redirect('dashboard_docente')
            elif user.rol == 'estudiante':
                return redirect('dashboard_estudiante')
            elif user.rol == 'directivo':
                return redirect('dashboard_directivo')
            elif user.rol == 'padre':
                return redirect('dashboard_padre')
            else:
                return redirect('/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_admin(request):
    hoy = timezone.now().date()
    # Asistencias de hoy
    asistencias_hoy = Asistencia.objects.filter(fecha_hora__date=hoy).count()
    # Permisos pendientes
    permisos_pendientes = Permiso.objects.filter(estado_permiso='pendiente').count()
    # Estudiantes con faltas críticas (más de FALTAS_NOTIFICACION faltas injustificadas en el mes)
    inicio_mes = hoy.replace(day=1)
    limite = settings.FALTAS_NOTIFICACION
    estudiantes_criticos = []
    for est in Estudiante.objects.all():
        faltas = Asistencia.objects.filter(
            estudiante=est,
            fecha_hora__date__gte=inicio_mes,
            estado_asistencia__in=['ausente', 'tarde']
        ).count()
        if faltas > limite:
            estudiantes_criticos.append(est)

    context = {
        'asistencias_hoy': asistencias_hoy,
        'permisos_pendientes': permisos_pendientes,
        'estudiantes_criticos_count': len(estudiantes_criticos),
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
@role_required('docente')
def dashboard_docente(request):
    docente = Docente.objects.get(usuario=request.user)
    curso_tutor = Curso.objects.filter(docente_tutor=docente).first()
    hoy = timezone.now().date()
    asistencias_curso = 0
    total_estudiantes = 0
    if curso_tutor:
        total_estudiantes = Estudiante.objects.filter(curso=curso_tutor).count()
        asistencias_curso = Asistencia.objects.filter(
            estudiante__curso=curso_tutor,
            fecha_hora__date=hoy
        ).count()
    context = {
        'curso_tutor': curso_tutor,
        'asistencias_curso': asistencias_curso,
        'total_estudiantes': total_estudiantes,
    }
    return render(request, 'dashboard/docente.html', context)

@login_required
@role_required('estudiante')
def dashboard_estudiante(request):
    estudiante = Estudiante.objects.get(usuario=request.user)
    hoy = timezone.now().date()
    # Porcentaje de asistencia general
    total_registros = Asistencia.objects.filter(estudiante=estudiante).count()
    presentes = Asistencia.objects.filter(estudiante=estudiante, estado_asistencia='presente').count()
    porcentaje = round((presentes / total_registros * 100) if total_registros > 0 else 0)
    # Última marcación
    ultima = Asistencia.objects.filter(estudiante=estudiante).order_by('-fecha_hora').first()
    context = {
        'porcentaje': porcentaje,
        'ultima': ultima,
    }
    return render(request, 'dashboard/estudiante.html', context)

@login_required
@role_required('directivo')
def dashboard_directivo(request):
    total_docentes = Docente.objects.count()
    total_administrativos = Administrativo.objects.count()
    total_personal = total_docentes + total_administrativos
    context = {
        'total_personal': total_personal,
    }
    return render(request, 'dashboard/directivo.html', context)

@login_required
@role_required('padre')
def dashboard_padre(request):
    hijos = PadreEstudiante.objects.filter(padre=request.user).select_related('estudiante__usuario')
    notificaciones_no_leidas = Notificacion.objects.filter(destinatario=request.user, leido=False).count()
    context = {
        'hijos_count': hijos.count(),
        'notificaciones_no_leidas': notificaciones_no_leidas,
    }
    return render(request, 'dashboard/padre.html', context)

@login_required
def home_redirect(request):
    # Redirigir al dashboard según rol si está autenticado
    user = request.user
    if user.rol == 'administrativo':
        return redirect('dashboard_admin')
    elif user.rol == 'docente':
        return redirect('dashboard_docente')
    # ... resto similar
    return redirect('login')

@login_required
def perfil(request):
    user = request.user
    if request.method == 'POST':
        # Actualizar campos editables
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip() or None  # vacío → None
        user.ci = request.POST.get('ci', '').strip()
        user.fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
        user.telefono = request.POST.get('telefono', '').strip()
        user.direccion = request.POST.get('direccion', '').strip()
        user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')

    # GET: mostrar formulario con datos actuales
    context = {
        'qr_uuid': str(user.qr_code),  # pasamos el UUID para generar QR
    }
    return render(request, 'usuarios/perfil.html', context)

#vista de url para cambio de contraseña
class PasswordChangeView(AuthPasswordChangeView):
    template_name = 'usuarios/password_change.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Al cambiar la contraseña, desmarcar el flag
        self.request.user.debe_cambiar_contrasena = False
        self.request.user.save()
        return response
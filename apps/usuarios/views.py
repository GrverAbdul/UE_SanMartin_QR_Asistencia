"""
Vistas de autenticación y dashboard.
apps/usuarios/views.py
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordChangeView as AuthPasswordChangeView
from django.urls import reverse_lazy

    
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
    return render(request, 'dashboard/admin.html')

@login_required
@role_required('docente')
def dashboard_docente(request):
    return render(request, 'dashboard/docente.html')

@login_required
@role_required('estudiante')
def dashboard_estudiante(request):
    return render(request, 'dashboard/estudiante.html')

@login_required
@role_required('directivo')
def dashboard_directivo(request):
    return render(request, 'dashboard/directivo.html')

@login_required
@role_required('padre')
def dashboard_padre(request):
    return render(request, 'dashboard/padre.html')

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
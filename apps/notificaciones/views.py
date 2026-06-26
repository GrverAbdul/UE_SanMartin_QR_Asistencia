"""
Vistas de notificaciones
apps/notificaciones/views.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notificacion

@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user).order_by('-fecha_envio')
    return render(request, 'notificaciones/lista.html', {'notificaciones': notificaciones})
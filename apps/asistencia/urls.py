"""
Rutas de asistencia.
Ubicación: apps/asistencia/urls.py
"""
from django.urls import path
from . import views


urlpatterns = [
    path('escaner/', views.escaner_view, name='escaner'),
    path('registrar_qr/', views.registrar_asistencia_qr, name='registrar_qr'),
    path('manual/', views.registro_manual, name='registro_manual'),
    path('historial/', views.historial, name='historial_asistencia'),
    path('admin/hoy/', views.admin_asistencias_hoy, name='admin_asistencias_hoy'),
path('admin/faltas-criticas/', views.admin_faltas_criticas, name='admin_faltas_criticas'),
]
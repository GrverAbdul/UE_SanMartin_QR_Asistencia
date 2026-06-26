"""
Rutas de permisos
apps/permisos/urls.py
"""
from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/', views.solicitar_permiso, name='solicitar_permiso'),
    path('lista/', views.lista_permisos, name='lista_permisos'),
    path('aprobar/<int:permiso_id>/', views.aprobar_permiso, name='aprobar_permiso'),
]
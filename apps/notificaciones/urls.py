"""
Rutas de notificaciones.
apps/notificaciones/urls.py
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notificaciones, name='lista_notificaciones'),
]
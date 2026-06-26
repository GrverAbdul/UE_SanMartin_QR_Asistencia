#Rutas de reportes
#apps/reportes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generar/', views.generador_reportes, name='generar_reporte'),
    path('get_estudiantes/', views.get_estudiantes_curso, name='get_estudiantes_curso'),
]
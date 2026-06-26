"""
Rutas de usuarios.
apps/usuarios/urls.py
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('', views.home_redirect, name='home'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/docente/', views.dashboard_docente, name='dashboard_docente'),
    path('dashboard/estudiante/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('dashboard/directivo/', views.dashboard_directivo, name='dashboard_directivo'),
    path('dashboard/padre/', views.dashboard_padre, name='dashboard_padre'),
    path('perfil/', views.perfil, name='perfil'),
]
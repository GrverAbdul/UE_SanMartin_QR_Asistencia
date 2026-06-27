#Configuración del admin para modelos de usuario y perfiles.
# apps/usuarios/admin.py
from .forms import UsuarioCreationForm, UsuarioChangeForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Estudiante, Docente, Administrativo, Curso, Materia, PadreEstudiante

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Perfil Estudiante'

class DocenteInline(admin.StackedInline):
    model = Docente
    can_delete = False
    verbose_name_plural = 'Perfil Docente'

class AdministrativoInline(admin.StackedInline):
    model = Administrativo
    can_delete = False
    verbose_name_plural = 'Perfil Administrativo'

class PadreEstudianteInline(admin.TabularInline):
    model = PadreEstudiante
    fk_name = 'padre'
    extra = 1
    verbose_name = "Hijo"
    verbose_name_plural = "Hijos"

# Modifica UsuarioAdmin para incluir el inline cuando el rol es 'padre'
# En la clase UsuarioAdmin, añade al método get_inlines:
    def get_inlines(self, request, obj):
        if obj:
            if obj.rol == 'estudiante':
                return [EstudianteInline]
            elif obj.rol == 'docente':
                return [DocenteInline]
            elif obj.rol == 'administrativo':
                return [AdministrativoInline]
            elif obj.rol == 'padre':
                return [PadreEstudianteInline]
        return []

@admin.register(PadreEstudiante)
class PadreEstudianteAdmin(admin.ModelAdmin):
    list_display = ('padre', 'estudiante', 'curso_del_estudiante')
    list_filter = ('padre',)

    def curso_del_estudiante(self, obj):
        return obj.estudiante.curso
    curso_del_estudiante.short_description = 'Curso'
    
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    list_display = ('username', 'email', 'rol', 'ci', 'is_active', 'debe_cambiar_contrasena')
    # Campos de solo lectura (el QR no se edita manualmente)
    readonly_fields = ('qr_code',)

    fieldsets = (
    (None, {
        'fields': ('username', 'password')
    }),
    ('Información personal', {
        'fields': ('first_name', 'last_name', 'email', 'ci', 'fecha_nacimiento', 'telefono', 'direccion', 'qr_code', 'debe_cambiar_contrasena')
    }),
    ('Permisos', {
        'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
    }),
    ('Fechas importantes', {
        'fields': ('last_login', 'date_joined')
    }),
    ('Rol', {
        'fields': ('rol',)
    }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'email', 'ci', 'fecha_nacimiento', 'telefono', 'direccion', 'rol', 'debe_cambiar_contrasena'),
        }),
    )

    def get_inlines(self, request, obj):
        if obj:
            if obj.rol == 'estudiante':
                return [EstudianteInline]
            elif obj.rol == 'docente':
                return [DocenteInline]
            elif obj.rol == 'administrativo':
                return [AdministrativoInline]
        return []

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'codigo_estudiante', 'curso')

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'profesionalidad', 'especialidad')

@admin.register(Administrativo)
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paralelo', 'turno', 'docente_tutor')

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


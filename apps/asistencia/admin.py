# apps/asistencia/admin.py
from django.contrib import admin
from .models import Asistencia

class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'tipo_usuario', 'persona_nombre', 'estado_asistencia')
    list_filter = ('tipo_usuario', 'estado_asistencia', 'fecha_hora')
    search_fields = ('estudiante__usuario__first_name', 'docente__usuario__first_name',
                     'administrativo__usuario__first_name', 'estudiante__usuario__last_name')

    # fecha_hora es no editable -> solo lectura
    readonly_fields = ('fecha_hora',)

    def persona_nombre(self, obj):
        if obj.estudiante:
            return obj.estudiante.usuario.get_full_name()
        elif obj.docente:
            return obj.docente.usuario.get_full_name()
        elif obj.administrativo:
            return obj.administrativo.usuario.get_full_name()
        return "—"
    persona_nombre.short_description = 'Persona'

    # Mostrar únicamente los campos del rol que corresponde
    def get_fieldsets(self, request, obj=None):
        # Campos comunes a todas las asistencias
        comunes = ('usuario_registro', 'tipo_usuario', 'fecha_hora', 'estado_asistencia', 'observacion')
        if obj is not None:
            if obj.tipo_usuario == 'estudiante':
                rol_field = ('estudiante',)
            elif obj.tipo_usuario == 'docente':
                rol_field = ('docente',)
            elif obj.tipo_usuario == 'administrativo':
                rol_field = ('administrativo',)
            else:
                rol_field = ('estudiante', 'docente', 'administrativo')  # fallback
        else:
            rol_field = ('estudiante', 'docente', 'administrativo')  # al crear nuevo

        return (
            (None, {
                'fields': comunes + rol_field
            }),
        )

admin.site.register(Asistencia, AsistenciaAdmin)
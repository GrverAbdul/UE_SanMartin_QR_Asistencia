"""
Decoradores para restringir acceso por rol.
apps/usuarios/decorators.py
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def in_roles(user):
        if user.is_authenticated and user.rol in roles:
            return True
        raise PermissionDenied
    return user_passes_test(in_roles)
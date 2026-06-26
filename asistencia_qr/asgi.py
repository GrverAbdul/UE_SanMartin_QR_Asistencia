#ASGI config
#asistencia_qr/asgi.py

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asistencia_qr.settings')
application = get_asgi_application()
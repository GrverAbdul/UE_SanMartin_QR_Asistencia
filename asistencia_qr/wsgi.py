#WSGI config para despliegue.
#asistencia_qr/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asistencia_qr.settings')
application = get_wsgi_application()
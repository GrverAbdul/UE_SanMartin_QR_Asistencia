#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recoger archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate
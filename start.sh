#!/usr/bin/env sh
set -eu

python manage.py migrate --noinput
exec python -m gunicorn AdminPay.wsgi:application --bind "0.0.0.0:${PORT:-10000}"

"""
ASGI config for restarter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from uvicorn import workers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restarter.settings')

application = get_asgi_application()


class UvicornH11Worker(workers.UvicornWorker):
    CONFIG_KWARGS = {"loop": "uvloop", "http": "httptools", "lifespan": "off"}

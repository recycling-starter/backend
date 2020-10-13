from multiprocessing import cpu_count

name = 'restarter'
max_requests = 1024

worker_class = 'restarter.asgi.UvicornH11Worker'

bind = "0.0.0.0:8000"
workers = cpu_count() + 1

env = {
    'DJANGO_SETTINGS_MODULE': 'restarter.settings'
}

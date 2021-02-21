from celery import Celery

from restarter import settings

app = Celery('restarter')
app.config_from_object(settings, namespace='CELERY')


@app.task()
def backup_bd():
    from django.core.management import call_command
    call_command('dbbackup', '--clean')


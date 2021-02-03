from celery import Celery
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from smtplib import SMTPException

from v1.apps.boxes.models import Box
from v1.apps.dropoffs.models import DropoffCall, DropoffLog
from restarter import settings


app = Celery('dropoffs', broker='reids://guest@localhost//')


@app.task
def call_dropoff(building):
    #  Отправка сообщения
    organization = building.organization
    nearly_full_boxes = list(Box.objects.filter(
        fullness__gte=organization.min_fullness_level_dropoff,
        building=building
    ))
    dropoff_call = DropoffCall(building=building)
    dropoff_call.save()

    dropofflog = []
    for box in nearly_full_boxes:
        dropofflog.append(DropoffLog(
            call=dropoff_call,
            box=box,
            box_percent_dropped=box.fullness
        ))
    DropoffLog.objects.bulk_create(dropofflog)

    message = render_to_string('dropoff_call.html', {
        'dropofflog': dropofflog,
        'building': building
    })
    email = EmailMessage(
        'Вывоз макулатуры RCS',
        message,
        to=[organization.dropoff_email_to],
        from_email=settings.EMAIL_FROM
    )
    email.content_subtype = "html"

    try:
        email.send()
        dropoff_call.is_sent = True
        dropoff_call.save()
    except SMTPException:
        pass

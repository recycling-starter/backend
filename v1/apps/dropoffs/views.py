# Create your views here.
from datetime import datetime, date, time
from smtplib import SMTPException

from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django_q.tasks import schedule
from django_q.models import Schedule
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from restarter import settings
from v1.apps.dropoffs.models import DropoffCall, DropoffLog
from v1.apps.dropoffs.serializers import DropoffListSerializer, DropoffDataSerializer


def call_dropoff(dropoff):
    #  Отправка сообщения
    #  Не уверен, что эта функция должна быть здесь
    message = render_to_string('dropoff_call.html', {
            'dropofflog': list(DropoffLog.objects.filter(call=dropoff)),
            'building': dropoff.building
        })
    email = EmailMessage(
        'Вывоз макулатуры RCS',
        message,
        to=[dropoff.building.organization.dropoff_email_to],
        from_email=settings.EMAIL_FROM
    )
    email.content_subtype = "html"

    try:
        email.send()
        dropoff.is_sent = True
        dropoff.save()
    except SMTPException:
        pass


class DropoffView(viewsets.ViewSet):
    def list(self, request):
        if not request.user or \
                request.user.organization is None:
            return Response(status=403)

        queryset = DropoffCall.objects.filter(building__organization=request.user.organization)
        serializer = DropoffListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not request.user or \
                request.user.organization is None:
            return Response(status=403)

        try:
            queryset = DropoffCall.objects.get(pk=pk, building__organization=request.user.organization)
        except DropoffCall.DoesNotExist:
            raise Http404
        serializer = DropoffDataSerializer(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if not request.user or request.user.organization is None:
            return Response(status=403)

        dropoff = get_object_or_404(
            DropoffCall, pk=pk,
            building__organization=request.user.organization)

        if dropoff.datetime_dropoff:
            return ValidationError('Already dropped off')

        if not dropoff.is_sent:
            d = date.today()
            t = time(19, 00)
            next_run = datetime.combine(d, t)
            schedule('views.call_dropoff',
                     dropoff,
                     schedule_type=Schedule.ONCE,
                     next_run=next_run)

        else:
            dropoff.is_dropped = True  # Такого параметра нет у модели, зачем эта строчка?
            dropoff.datetime_dropoff = timezone.make_aware(datetime.today())
            dropoff.save()
            for dropofflog in list(DropoffLog.objects.filter(call=dropoff)):
                dropofflog.box.fullness = 0
                dropofflog.box.save()
        return Response(status=status.HTTP_200_OK)

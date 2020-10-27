# Create your views here.
from datetime import datetime
from smtplib import SMTPException

from django.core.mail import EmailMessage
from django.http import Http404
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from restarter import settings
from v1.apps.dropoffs.models import DropoffCall, DropoffLog
from v1.apps.dropoffs.serializers import DropoffListSerializer, DropoffDataSerializer


class DropoffView(viewsets.ViewSet):
    def list(self, request):
        queryset = DropoffCall.objects.filter(building__organization=request.user.organization)
        serializer = DropoffListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = DropoffCall.objects.get(pk=pk)
        except DropoffCall.DoesNotExist:
            raise Http404
        serializer = DropoffDataSerializer(queryset)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            queryset = DropoffCall.objects.get(pk=pk)
        except DropoffCall.DoesNotExist:
            raise Http404
        if queryset.datetime_dropoff is not None:
            return ValidationError('Is already')
        if not queryset.is_sent:
            message = render_to_string('dropoff_call.html', {
                'dropofflog': list(DropoffLog.objects.filter(call=queryset)),
                'building': queryset.building
            })
            email = EmailMessage(
                'Вывоз макулатуры RCS',
                message,
                to=[queryset.building.organization.dropoff_email_to],
                from_email=settings.EMAIL_FROM
            )
            email.content_subtype = "html"
            try:
                email.send()
                queryset.is_sent = True
            except SMTPException:
                pass
        else:
            queryset.is_dropped = True
            queryset.datetime_dropoff = timezone.make_aware(datetime.today())
            queryset.save()
            for dropofflog in list(DropoffLog.objects.filter(call=queryset)):
                dropofflog.box.fullness = 0
                dropofflog.box.save()
        return Response(status=status.HTTP_201_CREATED)

# Create your views here.
from datetime import datetime

from django.http import Http404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from v1.apps.dropoffs.models import DropoffCall
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
        if queryset.is_dropped:
            return ValidationError('Is already')
        queryset.is_dropped = True
        queryset.datetime_dropoff = timezone.make_aware(datetime.today())
        queryset.save()
        return Response(status=status.HTTP_201_CREATED)

# Create your views here.
from django.core.mail import send_mail
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from restarter import settings
from v1.apps.boxes.models import Box
from v1.apps.boxes.serializers import BoxSerializer, BoxListSerializer, BoxDataSerializer, AvailableUsersSerializer
from v1.apps.dropoffs.models import DropoffCall, DropoffLog
from v1.apps.organizations.models import Building
from v1.apps.users.models import User


class BoxView(viewsets.ViewSet):
    def get_object(self, request, pk):
        queryset = Box.objects.all()
        box = get_object_or_404(queryset, pk=pk)
        return box

    def list(self, request):
        if request.user.organization is not None:
            if 'building' in request.query_params:
                building = request.query_params['building']
                try:
                    building = Building.objects.get(pk=building)
                except Building.DoesNotExist:
                    raise Http404
                queryset = Box.objects.filter(
                    building=building
                )
            else:
                queryset = Box.objects.filter(
                    building__organization=request.user.organization
                )
        else:
            queryset = request.user.box_set.all()
        serializer = BoxListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if 'building' not in request.data or 'room' not in request.data:
            raise ValidationError('Not enough data')
        try:
            building = Building.objects.get(pk=request.data['building'])
        except Building.DoesNotExist:
            raise Http404
        box = Box(
            room=request.data['room'],
            building=building,
        )
        box.save()
        return Response(BoxSerializer(box).data)

    def retrieve(self, request, pk=None):
        box = self.get_object(request, pk)
        return Response(BoxDataSerializer(box).data)

    def update(self, request, pk):
        box = self.get_object(request, pk)
        serializer = BoxSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        box.fullness = serializer.validated_data['fullness']
        box.room = serializer.validated_data['room']

        box.save()

        building = box.building
        organization = building.organization
        full_boxes = list(Box.objects.filter(
            fullness__gte=organization.min_fullness_level_dropoff_call,
            building=building
        ))
        nearly_full_boxes = list(Box.objects.filter(
            fullness__gte=organization.min_fullness_level_dropoff,
            building=building
        ))
        if box.fullness >= organization.min_fullness_level_dropoff_call \
                and len(full_boxes) >= organization.min_full_boxes:
            try:
                dropoff_call = DropoffCall.objects.get(
                    building=box.building
                )
            except DropoffCall.DoesNotExist:
                send_mail(
                    subject='Нужен вывоз мусора',
                    message='Привет пока',
                    recipient_list=[box.building.organization.dropoff_email_to],
                    from_email=settings.EMAIL_HOST_USER,
                    fail_silently=False
                )
                dropoff_call = DropoffCall(
                    building=box.building
                )
                dropoff_call.save()
                dropofflog = []
                for i in nearly_full_boxes:
                    dropofflog.append(DropoffLog(
                        call=dropoff_call,
                        box=i,
                        box_percent_dropped=i.fullness
                    ))
                DropoffLog.objects.bulk_create(dropofflog)

        return Response(BoxSerializer(box).data)

    def partial_update(self, request, pk):
        queryset = request.user.box_set.all()
        box = get_object_or_404(queryset, pk=pk)

        if 'fullness' in request.data:
            fullness = request.data['fullness']
            try:
                fullness = int(fullness)
            except ValueError:
                raise ValidationError(detail=_('"fullness" must be int.'))
        else:
            raise ValidationError(detail=_('Must include "fullness".'))

        if fullness < box.fullness:
            raise PermissionDenied
        if fullness > 100:
            raise ValidationError(detail=_('"fullness" must be less than 100.'))

        box.fullness = fullness
        box.save()

        building = box.building
        organization = building.organization
        full_boxes = list(Box.objects.filter(
            fullness__gte=organization.min_fullness_level_dropoff_call,
            building=building
        ))
        nearly_full_boxes = list(Box.objects.filter(
            fullness__gte=organization.min_fullness_level_dropoff,
            building=building
        ))
        if box.fullness >= organization.min_fullness_level_dropoff_call \
                and len(full_boxes) >= organization.min_full_boxes:
            try:
                dropoff_call = DropoffCall.objects.get(
                    building=box.building
                )
            except DropoffCall.DoesNotExist:
                send_mail(
                    subject='Нужен вывоз мусора',
                    message='Привет пока',
                    recipient_list=[box.building.organization.dropoff_email_to],
                    from_email=settings.EMAIL_HOST_USER,
                    fail_silently=False
                )
                dropoff_call = DropoffCall(
                    building=box.building
                )
                dropoff_call.save()
                dropofflog = []
                for i in nearly_full_boxes:
                    dropofflog.append(DropoffLog(
                        call=dropoff_call,
                        box=i,
                        box_percent_dropped=i.fullness
                    ))
                DropoffLog.objects.bulk_create(dropofflog)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        box = self.get_object(request, pk)
        box.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        box = self.get_object(request, pk)

        if 'user' not in request.data:
            raise ValidationError(_('"user" must be here'))

        user = request.data['user']

        try:
            user = User.objects.get(pk=user)
            if user.building != box.building:
                raise ValidationError(_('"user" in wrong building'))
        except User.DoesNotExist:
            raise ValidationError(_('"user" invalid'))

        if user not in box.users.all():
            box.users.add(user)
        else:
            raise ValidationError(_('"user" is already in box'))

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def get_users_available(self, request, pk=None):
        box = self.get_object(request, pk)
        users = User.objects.annotate(count=Count('box')).filter(building=box.building).exclude(box=box).order_by('count')
        return Response(AvailableUsersSerializer(users, many=True).data)

    @add_user.mapping.delete
    def delete_user(self, request, pk=None):
        try:
            box = Box.objects.get(pk=pk)
        except Box.DoesNotExist:
            raise Http404
        if 'user' not in request.query_params:
            raise ValidationError(_('"user" must be here'))
        user = request.query_params['user']
        try:
            user = User.objects.get(pk=user)
            if user.building != box.building:
                raise ValidationError(_('"user" in wrong building'))
            if user.building.organization != request.user.organization:
                raise PermissionDenied
        except User.DoesNotExist:
            raise ValidationError(_('"user" invalid'))
        if user not in box.users.all():
            raise ValidationError(_('"user" is not yet in box'))
        else:
            box.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


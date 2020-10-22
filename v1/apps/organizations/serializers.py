from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from restarter import settings
from v1.apps.boxes.models import Box
from v1.apps.dropoffs.models import DropoffCall, DropoffLog
from v1.apps.organizations.models import Organization, Building


class OrganizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'avatar', 'name']


class BuildingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'address', 'organization']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['min_full_boxes',
                  'min_fullness_level_dropoff_call',
                  'min_fullness_level_dropoff',
                  'dropoff_email_to',
                  'dropoff_email_from']


    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        for box in list(Box.objects.filter(organzation=instance)):
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
                    _ = DropoffCall.objects.get(
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

        return instance

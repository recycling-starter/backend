from rest_framework import serializers

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

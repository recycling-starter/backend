from rest_framework import serializers

from v1.apps.boxes.models import Box
from v1.apps.users.models import User


class BoxListSerializer(serializers.ModelSerializer):
    building = serializers.SerializerMethodField('get_building')

    def get_building(self, obj):
        return {
            'id': obj.building.id,
            'address': obj.building.address
        }

    class Meta:
        model = Box
        fields = ['id', 'fullness', 'room', 'building']
        read_only_fields = ['id', 'fullness']



class AvailableUsersSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField('get_count')

    def get_count(self, obj):
        return len(obj.box_set.all())

    class Meta:
        model = User
        fields = ['id', 'first_name', 'room', 'count']


class BoxDataSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField('get_users')
    building = serializers.SerializerMethodField('get_building')

    def get_users(self, obj):
        return [{
            'id': i.id,
            'first_name': i.first_name,
            'room': i.room
        } for i in obj.users.all()]

    def get_building(self, obj):
        return {
            'id': obj.building.id,
            'address': obj.building.address
        }

    class Meta:
        model = Box
        fields = ['id', 'fullness', 'room', 'building', 'users']


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id',
                  'fullness',
                  'room',
                  'building']
        read_only_fields = ['id', 'building']

    def create(self, validated_data):
        box = Box(
            room=validated_data['room'],
            building=validated_data['building'],
        )
        box.save()
        return box

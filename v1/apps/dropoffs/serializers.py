from rest_framework import serializers

from v1.apps.dropoffs.models import DropoffCall, DropoffLog


class DropoffListSerializer(serializers.ModelSerializer):
    building = serializers.SerializerMethodField('get_building')

    def get_building(self, obj):
        return {
            'id': obj.building.id,
            'address': obj.building.address
        }

    class Meta:
        model = DropoffCall
        fields = '__all__'


class DropoffLogSerializer(serializers.ModelSerializer):
    box = serializers.SerializerMethodField('get_box')

    def get_box(self, obj):
        return {
            'id': obj.box.id,
            'room': obj.box.room,
            'box_percent_dropped': obj.box_percent_dropped
        }

    class Meta:
        model = DropoffLog
        fields = ['data']


class DropoffDataSerializer(serializers.ModelSerializer):
    building = serializers.SerializerMethodField('get_building')
    boxes = serializers.SerializerMethodField('get_boxes')

    def get_building(self, obj):
        return {
            'id': obj.building.id,
            'address': obj.building.address
        }

    def get_boxes(self, obj):
        return DropoffLogSerializer(DropoffLog.objects.filter(call=obj), many=True).data

    class Meta:
        model = DropoffCall
        fields = ['datetime_call', 'datetime_dropoff', 'building', 'is_dropped', 'boxes']

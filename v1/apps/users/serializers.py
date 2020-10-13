from rest_framework import serializers

from v1.apps.users.models import User


class UserListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'building', 'password', 'email', 'phone', 'room']

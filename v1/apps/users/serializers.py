from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from v1.apps.users.models import User


class UserListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'building', 'password', 'email', 'phone', 'room', 'organization']
        read_only_fields = ['id']


class UserDataSerializer(serializers.ModelSerializer):
    boxes = serializers.SerializerMethodField('get_boxes')

    def get_boxes(self, obj):
        return [{
            'id': i.id,
            'fullness': i.fullness,
            'room': i.room
        } for i in list(obj.box_set.all())]

    class Meta:
        model = User
        fields = ['id', 'first_name', 'building', 'email', 'phone', 'room', 'organization', 'boxes']
        read_only_fields = ['id', 'boxes']


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

from django.contrib.auth import authenticate
from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.views import ObtainAuthToken

from v1.apps.users.views import activate, UserView


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


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer


urlpatterns = [
    path('auth/', CustomObtainAuthToken.as_view()),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,35})/$', activate,
            name='activate'),
    path('', UserView.as_view({
        'post': 'create',
        'get': 'retrieve',
        'put': 'partial_update'
    })),
]

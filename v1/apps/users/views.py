from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from restarter.settings import DOMAIN, EMAIL_HOST_USER
from v1.apps.organizations.models import Building
from v1.apps.users.models import User, account_activation_token
from v1.apps.users.serializers import UserListCreateSerializer


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


class UserView(viewsets.ViewSet):
    def retrieve(self, request):
        result = UserListCreateSerializer(request.user).data
        del result['password']
        return Response(result)

    def create(self, request):
        serializer = UserListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = User(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            room=validated_data['room'],
            building=validated_data['building'],
            is_active=False
        )

        user.set_password(validated_data['password'])
        user.save()
        mail_subject = 'Activate your ReStarter account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': DOMAIN,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        email = EmailMessage(
            mail_subject, message, to=[validated_data['email']], from_email=EMAIL_HOST_USER
        )
        email.send()

        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        pass

    def partial_update(self, request):
        email = request.user.email
        phone = request.user.phone
        first_name = request.user.first_name
        room = request.user.room
        building = request.user.building
        if 'email' in request.data:
            email = request.data['email']
        if 'phone' in request.data:
            phone = request.data['phone']
        if 'first_name' in request.data:
            first_name = request.data['first_name']
        if 'room' in request.data:
            room = request.data['room']
        request.user.email = email
        request.user.phone = phone
        request.user.first_name = first_name
        request.user.room = room
        request.user.building = building
        try:
            request.user.save()
        except IntegrityError:
            raise ValidationError('this email already exists')
        result = UserListCreateSerializer(request.user).data
        del result['password']
        return Response(result)

    def destroy(self, request, pk):
        pass

from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from restarter.settings import EMAIL_HOST_USER, BASEDOMAIN, EMAIL_FROM
from v1.apps.organizations.models import Building, Organization
from v1.apps.users.models import User, account_activation_token
from v1.apps.users.serializers import UserListCreateSerializer, CustomAuthTokenSerializer, UserDataSerializer, \
    PasswordSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.id
        })


class UserView(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        if not request.user or \
                request.user.organization != user.building.organization or \
                request.user != user:
            return Response(status=403)
        result = UserDataSerializer(user).data
        return Response(result)

    def list(self, request):

        if not request.user or \
                request.user.organization is None:
            return Response(status=403)
        if 'organization' in request.query_params:
            try:
                organization = Organization.objects.get(id=request.query_params['organization'])
            except Organization.DoesNotExist:
                raise Http404
            queryset = User.objects.filter(building__organization=organization)
        elif 'building' in request.query_params:
            try:
                building = Building.objects.get(id=request.query_params['building'])
            except Building.DoesNotExist:
                raise Http404
            queryset = User.objects.filter(building=building)
        else:
            queryset = User.objects.all()

        result = UserListCreateSerializer(queryset, many=True).data
        for i in result:
            del i['password']
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
        mail_subject = 'Активируйте свой аккаунт ReStarter.'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'url': f'https://{BASEDOMAIN}/confirm_email/{str(uid)}/{str(token)}',
        })
        email = EmailMessage(
            mail_subject, message, to=[validated_data['email']], from_email=EMAIL_FROM
        )
        email.send()

        return Response(status=status.HTTP_201_CREATED)

    def update(self, request):
        if not request.user:
            return Response(status=403)
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        if not request.user:
            return Response(status=403)
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


    @action(detail=True, methods=['post'])
    def check_email(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            if 'password' in request.data:
                password = request.data['password']
                user.set_password(password)
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reset_password(self, request):
        if 'email' not in request.data:
            raise ValidationError('email not provided')

        try:
            user = User.objects.get(email=request.data['email'])

            mail_subject = 'Сброс пароля ReStarter.'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            message = render_to_string('reset_password.html', {
                'user': user,
                'url': f'https://{BASEDOMAIN}/reset_password/{str(uid)}/{str(token)}',
            })
            email = EmailMessage(
                mail_subject, message, to=[request.data['email']], from_email=EMAIL_FROM
            )
            email.send()
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        return Response(status=status.HTTP_201_CREATED)

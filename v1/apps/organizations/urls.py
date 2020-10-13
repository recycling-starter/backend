from django.urls import path
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from v1.apps.organizations.models import Organization, Building
from v1.apps.organizations.permissions import IsOrganizationAdmin
from v1.apps.organizations.serializers import OrganizationListSerializer, OrganizationSerializer, BuildingListSerializer
from v1.apps.organizations.views import BuildingView

urlpatterns = [
    path('', ListAPIView.as_view(
        queryset=Organization.objects.all(),
        serializer_class=OrganizationListSerializer,
        permission_classes=[IsAuthenticated]
    ),
         name='organization-list'),
    path('<int:pk>', RetrieveUpdateAPIView.as_view(
        queryset=Organization.objects.all(),
        serializer_class=OrganizationSerializer,
        permission_classes=[IsOrganizationAdmin]
    ),
         name='organization-RW'),
]

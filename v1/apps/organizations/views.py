# Create your views here.
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from v1.apps.organizations.models import Building
from v1.apps.organizations.serializers import BuildingListSerializer


class BuildingView(viewsets.ViewSet):
    def list(self, request):
        queryset = Building.objects.filter(organization=request.user.organization)
        serializer = BuildingListSerializer(queryset, many=True)
        return Response(serializer.data)

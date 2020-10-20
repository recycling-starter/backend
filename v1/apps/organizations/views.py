# Create your views here.
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response

from v1.apps.organizations.models import Building, Organization
from v1.apps.organizations.serializers import BuildingListSerializer


class BuildingView(viewsets.ViewSet):
    def list(self, request):
        if 'organization' in request.query_params:
            try:
                organization = Organization.objects.get(id=request.query_params['organization'])
            except Building.DoesNotExist:
                raise Http404
            queryset = Building.objects.filter(organization=organization)
        else:
            queryset = Building.objects.all()
        serializer = BuildingListSerializer(queryset, many=True)
        return Response(serializer.data)

from django.urls import path

from v1.apps.organizations.views import BuildingView

urlpatterns = [

    path('', BuildingView.as_view({
        'get': 'list',
    }),
         name='buildings-list')
]
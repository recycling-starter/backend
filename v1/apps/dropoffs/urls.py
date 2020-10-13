from django.urls import path

from v1.apps.dropoffs.views import DropoffView

urlpatterns = [
    path('', DropoffView.as_view({
        'get': 'list'
    })),
    path('<int:pk>', DropoffView.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
]

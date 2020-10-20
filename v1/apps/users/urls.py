from django.urls import path, re_path

from v1.apps.users.views import activate, UserView, CustomObtainAuthToken

urlpatterns = [
    path('auth/', CustomObtainAuthToken.as_view()),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,35})/$', activate,
            name='activate'),
    path('', UserView.as_view({
        'post': 'create',
        'get': 'list',
        'put': 'partial_update'
    })),
    path('<int:pk>', UserView.as_view({
        'get': 'retrieve',
    })),
]

from django.urls import path

from v1.apps.boxes.views import BoxView

urlpatterns = [
    path('', BoxView.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('<int:pk>', BoxView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('<int:pk>/get_available', BoxView.as_view({
        'get': 'get_users_available'
    })),
    path('<int:pk>/changeuser', BoxView.as_view({
        'post': 'add_user',
        'delete': 'delete_user',
    })),
]

from rest_framework.permissions import BasePermission

SAFE_METHODS = ['GET']


class IsAdminOrReadonly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                return True
            if request.user.organization is not None:
                return True
        return False


class IsOrganizationAdmin(BasePermission):
    def has_permission(self, request, view):
        if view.lookup_field in view.kwargs:
            if view.kwargs[view.lookup_field]:
                return (request.user
                        and request.user.is_authenticated
                        and request.user.organization is not None)
        return False

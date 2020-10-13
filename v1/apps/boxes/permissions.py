from rest_framework.permissions import BasePermission


class IsAuthenticatedOrAdmin(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method in ['PUT', 'DELETE'] and not request.user.is_staff:
                return False
            return True
        return False

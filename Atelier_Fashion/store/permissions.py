from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Read access for everyone; write access only for staff users."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

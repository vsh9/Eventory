from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_staff


class IsAdmin(BasePermission):
    """Permission class for College Staff (Admins)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsStudent(BasePermission):
    """Permission class for Students"""
    def has_permission(self, request, view):
        return request.user and not request.user.is_staff


class IsAuthenticated(BasePermission):
    """Permission class for any authenticated user (Admin or Student)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

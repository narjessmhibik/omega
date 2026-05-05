from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsTechnicien(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_technicien


class IsAdminOrSelf(BasePermission):
    """Admin voit tout, technicien voit uniquement ses propres données"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj == request.user
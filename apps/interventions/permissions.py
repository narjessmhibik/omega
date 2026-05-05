from rest_framework.permissions import BasePermission
from apps.accounts.permissions import IsAdmin


class PeutModifierIntervention(BasePermission):
    """Bloque la modification si l'intervention a plus de 24h"""
    def has_object_permission(self, request, view, obj):
        # Admin peut toujours modifier
        if request.user.is_admin:
            return True
        # Technicien : seulement si dans les 24h
        return obj.est_modifiable
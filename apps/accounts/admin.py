from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'telephone', 'est_actif']
    list_filter = ['role', 'est_actif']
    search_fields = ['username', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('OMEGA', {'fields': ('role', 'telephone', 'est_actif')}),
    )
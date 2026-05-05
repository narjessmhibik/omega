from django.contrib import admin
from .models import Constat


@admin.register(Constat)
class ConstatAdmin(admin.ModelAdmin):
    list_display = ['id', 'technicien', 'intervention', 'categorie', 'est_signe', 'date_creation']
    list_filter = ['categorie']
    search_fields = ['technicien__username', 'nom_signataire']
    readonly_fields = ['date_creation', 'date_signature']
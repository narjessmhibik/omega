from django.contrib import admin
from .models import (
    Operateur, TypeIntervention, StatutIntervention,
    BaremeTechnicien, BaremeOperateur, Intervention
)

admin.site.register(Operateur)
admin.site.register(TypeIntervention)
admin.site.register(StatutIntervention)
admin.site.register(BaremeTechnicien)
admin.site.register(BaremeOperateur)

@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket_id', 'technicien', 'operateur', 'type_intervention', 'statut', 'date_intervention']
    list_filter = ['operateur', 'type_intervention', 'statut']
    search_fields = ['ticket_id', 'technicien__username']
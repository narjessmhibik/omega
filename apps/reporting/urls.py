# apps/reporting/urls.py
from django.urls import path
from . import views
from .views import HistoriqueMensuelView, ExportExcelMoisView, HistoriqueMensuelTechView

urlpatterns = [
    path('dashboard/', views.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('techniciens/', views.StatsTechnicienView.as_view(), name='stats_techniciens'),
    path('me/', views.MonDashboardView.as_view(), name='mon_dashboard'),
    path('historique/', views.HistoriqueInterventionsView.as_view(), name='historique'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('historique-mensuel/', HistoriqueMensuelView.as_view()),
    path('historique-mensuel/tech/', HistoriqueMensuelTechView.as_view()),  # ← ajouter
    path('export/excel/<str:mois>/', ExportExcelMoisView.as_view()),
]
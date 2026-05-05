from django.urls import path
from . import views

urlpatterns = [
    # Listes
    path('operateurs/', views.OperateurListView.as_view()),
    path('operateurs/<int:pk>/', views.OperateurDetailView.as_view()),
    path('types/', views.TypeInterventionListView.as_view()),
    path('types/<int:pk>/', views.TypeInterventionDetailView.as_view()),
    path('statuts/', views.StatutListView.as_view()),
    path('statuts/<int:pk>/', views.StatutDetailView.as_view()),
    # Barèmes
    path('baremes/technicien/', views.BaremeTechnicienListView.as_view()),
    path('baremes/technicien/<int:pk>/', views.BaremeTechnicienDetailView.as_view()),
    path('baremes/operateur/', views.BaremeOperateurListView.as_view()),
    path('baremes/operateur/<int:pk>/', views.BaremeOperateurDetailView.as_view()),
    # Interventions
    path('', views.ListCreateInterventionView.as_view()),
    path('<int:pk>/', views.InterventionDetailView.as_view()),
]
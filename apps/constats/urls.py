# apps/constats/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCreateConstatView.as_view(), name='constat-list-create'),
    path('<int:pk>/', views.ConstatDetailView.as_view(), name='constat-detail'),
    path('<int:pk>/signer/', views.SignatureView.as_view(), name='constat-signature'),
    path('<int:pk>/soumettre/', views.SoumettreConstatView.as_view(), name='constat-soumettre'),
    path('<int:pk>/gerer/', views.GererConstatAdminView.as_view(), name='constat-gerer'),
    path('intervention/<int:intervention_id>/', views.ConstatParInterventionView.as_view(), name='constat-by-intervention'),
    path('categories/', views.ConstatCategoriesView.as_view(), name='constat-categories'),
    path('statut/<str:statut>/', views.ConstatsParStatutView.as_view(), name='constats-by-statut'),
    path('<int:pk>/recevoir-pdf/', views.RecevoirPDFView.as_view(), name='recevoir_pdf'),
]
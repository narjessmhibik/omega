from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCreateAnnonceView.as_view(), name='annonce-list'),
    path('derniere/', views.DerniereAnnonceView.as_view(), name='annonce-derniere'),
    path('<int:pk>/lue/', views.MarquerLueView.as_view(), name='annonce-lue'),
    path('privee/', views.AnnoncePriveeListCreateView.as_view(), name='annonce-privee-list'),
    path('privee/<int:pk>/lue/', views.MarquerAnnoncePriveeLueView.as_view(), name='annonce-privee-lue'),
]
# apps/accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# ✅ Plus de router gasoil ici — il est dans config/urls.py
router = DefaultRouter()
# (si vous aviez : router.register(r'gasoil', RechargeGasoilViewSet) → SUPPRIMER)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('users/', views.ListCreateUserView.as_view(), name='users_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/reset-password/', views.AdminChangePasswordView.as_view(), name='reset_password'),
] + router.urls
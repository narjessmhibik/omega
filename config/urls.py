# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter                  # ✅ AJOUTÉ
from apps.accounts.views import RechargeGasoilViewSet

# ✅ Définir le router AVANT de l'utiliser dans urlpatterns
api_router = DefaultRouter()
api_router.register(r'gasoil', RechargeGasoilViewSet, basename='gasoil')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', TemplateView.as_view(template_name='admin_panel.html'), name='panel'),
    path('api/', include(api_router.urls)),                        # → /api/gasoil/
    path('api/auth/', include('apps.accounts.urls')),
    path('api/interventions/', include('apps.interventions.urls')),
    path('api/constats/', include('apps.constats.urls')),
    path('api/reporting/', include('apps.reporting.urls')),
    path('api/annonces/', include('apps.annonces.urls')),
    path('', include('pwa.urls')),  # ← ajouter ça

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
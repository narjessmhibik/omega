from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    Intervention, Operateur, TypeIntervention,
    StatutIntervention, BaremeTechnicien, BaremeOperateur
)
from .serializers import (
    InterventionSerializer, CreateInterventionSerializer,
    OperateurSerializer, TypeInterventionSerializer,
    StatutInterventionSerializer, BaremeTechnicienSerializer,
    BaremeOperateurSerializer
)
from apps.accounts.permissions import IsAdmin


# ── LISTES (opérateurs, types, statuts) ──────────────

class OperateurListView(generics.ListCreateAPIView):
    queryset = Operateur.objects.all()
    serializer_class = OperateurSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]


class OperateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operateur.objects.all()
    serializer_class = OperateurSerializer
    permission_classes = [IsAdmin]


class TypeInterventionListView(generics.ListCreateAPIView):
    queryset = TypeIntervention.objects.all()
    serializer_class = TypeInterventionSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]


class TypeInterventionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TypeIntervention.objects.all()
    serializer_class = TypeInterventionSerializer
    permission_classes = [IsAdmin]


class StatutListView(generics.ListCreateAPIView):
    queryset = StatutIntervention.objects.all()
    serializer_class = StatutInterventionSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]


class StatutDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StatutIntervention.objects.all()
    serializer_class = StatutInterventionSerializer
    permission_classes = [IsAdmin]


# ── BARÈMES ──────────────────────────────────────────

class BaremeTechnicienListView(generics.ListCreateAPIView):
    queryset = BaremeTechnicien.objects.all()
    serializer_class = BaremeTechnicienSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]


class BaremeTechnicienDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BaremeTechnicien.objects.all()
    serializer_class = BaremeTechnicienSerializer
    permission_classes = [IsAdmin]


class BaremeOperateurListView(generics.ListCreateAPIView):
    serializer_class = BaremeOperateurSerializer

    def get_queryset(self):
        qs = BaremeOperateur.objects.all()
        operateur_id = self.request.query_params.get('operateur')
        if operateur_id:
            qs = qs.filter(operateur_id=operateur_id)
        return qs

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]


class BaremeOperateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BaremeOperateur.objects.all()
    serializer_class = BaremeOperateurSerializer
    permission_classes = [IsAdmin]


# ── INTERVENTIONS ────────────────────────────────────

class ListCreateInterventionView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Intervention.objects.all() if user.is_admin else Intervention.objects.filter(technicien=user)

        # Filtres
        technicien_id = self.request.query_params.get('technicien')
        operateur_id = self.request.query_params.get('operateur')
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')
        ticket = self.request.query_params.get('ticket')

        if technicien_id:
            qs = qs.filter(technicien_id=technicien_id)
        if operateur_id:
            qs = qs.filter(operateur_id=operateur_id)
        if date_debut:
            qs = qs.filter(date_intervention__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(date_intervention__date__lte=date_fin)
        if ticket:
            qs = qs.filter(ticket_id__icontains=ticket)
        return qs

    def get_serializer_class(self):
        return CreateInterventionSerializer if self.request.method == 'POST' else InterventionSerializer


class InterventionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Intervention.objects.all() if user.is_admin else Intervention.objects.filter(technicien=user)

    def update(self, request, *args, **kwargs):
        intervention = self.get_object()
        if not intervention.est_modifiable and not request.user.is_admin:
            return Response(
                {'detail': 'Modification impossible : délai de 24h dépassé.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
# apps/constats/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Constat
from .serializers import ConstatSerializer, CreateConstatSerializer, SignatureSerializer
from apps.accounts.permissions import IsAdmin


class ListCreateConstatView(generics.ListCreateAPIView):
    """
    GET  /api/constats/  — liste les constats
    POST /api/constats/  — créer un constat avec photo
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Constat.objects.all().order_by('-date_creation')
        return Constat.objects.filter(technicien=user).order_by('-date_creation')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateConstatSerializer
        return ConstatSerializer
    
    def perform_create(self, serializer):
        serializer.save(technicien=self.request.user)


class ConstatDetailView(generics.RetrieveAPIView):
    """GET /api/constats/<id>/ — détail d'un constat"""
    serializer_class = ConstatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Constat.objects.all()
        return Constat.objects.filter(technicien=user)


class SignatureView(APIView):
    """
    POST /api/constats/<id>/signer/ — le client signe le constat
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            constat = Constat.objects.get(pk=pk)
        except Constat.DoesNotExist:
            return Response({'detail': 'Constat introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier que c'est le technicien du constat
        if not request.user.is_admin and constat.technicien != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        if constat.est_signe:
            return Response({'detail': 'Ce constat est déjà signé.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        constat.signer(
            nom_signataire=serializer.validated_data['nom_signataire'],
            signature=serializer.validated_data['signature']
        )

        return Response({'detail': 'Signature enregistrée avec succès.', 'id': constat.id}, status=status.HTTP_200_OK)


class ConstatParInterventionView(generics.ListAPIView):
    """GET /api/constats/intervention/<id>/ — tous les constats d'une intervention"""
    serializer_class = ConstatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        intervention_id = self.kwargs['intervention_id']
        user = self.request.user
        if user.is_admin:
            return Constat.objects.filter(intervention_id=intervention_id)
        return Constat.objects.filter(intervention_id=intervention_id, technicien=user)


class ConstatCategoriesView(APIView):
    """GET /api/constats/categories/ — liste des catégories"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = [
            {'value': 'litige_client', 'label': 'Litige client'},
            {'value': 'litige_operateur', 'label': 'Litige opérateur'},
            {'value': 'probleme_materiel', 'label': 'Problème matériel'},
            {'value': 'incident_terrain', 'label': 'Incident terrain'},
            {'value': 'client_absent', 'label': 'Client absent'},
            {'value': 'acces_refuse', 'label': 'Accès refusé'},
            {'value': 'autre', 'label': 'Autre'},
        ]
        return Response(categories)
    
# apps/constats/views.py (ajoutez ces nouvelles classes)
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Constat
from .serializers import (
    ConstatSerializer, CreateConstatSerializer, SignatureSerializer,
    SoumettreConstatSerializer, ValiderConstatSerializer
)
from apps.accounts.permissions import IsAdmin


class ListCreateConstatView(generics.ListCreateAPIView):
    """
    GET  /api/constats/  — liste les constats
    POST /api/constats/  — créer un constat avec photo
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Constat.objects.all().order_by('-date_creation')
        return Constat.objects.filter(technicien=user).order_by('-date_creation')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateConstatSerializer
        return ConstatSerializer
    
    def perform_create(self, serializer):
        serializer.save(technicien=self.request.user)


class ConstatDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET /api/constats/<id>/ — détail d'un constat"""
    serializer_class = ConstatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Constat.objects.all()
        return Constat.objects.filter(technicien=user)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SignatureView(APIView):
    """
    POST /api/constats/<id>/signer/ — le client signe le constat
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            constat = Constat.objects.get(pk=pk)
        except Constat.DoesNotExist:
            return Response({'detail': 'Constat introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_admin and constat.technicien != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        if constat.est_signe:
            return Response({'detail': 'Ce constat est déjà signé.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        constat.signer(
            nom_signataire=serializer.validated_data['nom_signataire'],
            signature=serializer.validated_data['signature']
        )

        return Response({'detail': 'Signature enregistrée avec succès.', 'id': constat.id}, status=status.HTTP_200_OK)


class ConstatParInterventionView(generics.ListAPIView):
    """GET /api/constats/intervention/<id>/ — tous les constats d'une intervention"""
    serializer_class = ConstatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        intervention_id = self.kwargs['intervention_id']
        user = self.request.user
        if user.is_admin:
            return Constat.objects.filter(intervention_id=intervention_id)
        return Constat.objects.filter(intervention_id=intervention_id, technicien=user)


class ConstatCategoriesView(APIView):
    """GET /api/constats/categories/ — liste des catégories"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = [
            {'value': 'litige_client', 'label': 'Litige client'},
            {'value': 'litige_operateur', 'label': 'Litige opérateur'},
            {'value': 'probleme_materiel', 'label': 'Problème matériel'},
            {'value': 'incident_terrain', 'label': 'Incident terrain'},
            {'value': 'client_absent', 'label': 'Client absent'},
            {'value': 'acces_refuse', 'label': 'Accès refusé'},
            {'value': 'autre', 'label': 'Autre'},
        ]
        return Response(categories)


# ========== NOUVELLES VUES POUR LA SOUMISSION ==========

class SoumettreConstatView(APIView):
    """
    POST /api/constats/<id>/soumettre/ — le technicien soumet le constat à l'admin
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            constat = Constat.objects.get(pk=pk)
        except Constat.DoesNotExist:
            return Response({'detail': 'Constat introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier que c'est le technicien du constat
        if constat.technicien != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        # === MODIFICATION ICI : Signature optionnelle ===
        # On ne vérifie plus la signature obligatoire
        # if not constat.est_signe:
        #     return Response({'detail': 'Le constat doit être signé avant soumission.'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier qu'il n'est pas déjà soumis
        if constat.statut != 'brouillon':
            return Response({'detail': f'Ce constat est déjà {constat.get_statut_display()}.'}, status=status.HTTP_400_BAD_REQUEST)

        constat.soumettre()
        
        return Response({
            'detail': 'Constat soumis avec succès à l\'administrateur.',
            'id': constat.id,
            'statut': constat.statut,
            'date_soumission': constat.date_soumission
        }, status=status.HTTP_200_OK)

class GererConstatAdminView(APIView):
    """
    POST /api/constats/<id>/gerer/ — l'admin valide ou rejette le constat
    Body: {"action": "valider" ou "rejeter", "commentaire": "optionnel"}
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            constat = Constat.objects.get(pk=pk)
        except Constat.DoesNotExist:
            return Response({'detail': 'Constat introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ValiderConstatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        commentaire = serializer.validated_data.get('commentaire', '')

        if action == 'valider':
            constat.valider(commentaire)
            message = 'Constat validé avec succès.'
        elif action == 'rejeter':
            if not commentaire:
                return Response({'detail': 'Un commentaire est requis pour rejeter le constat.'}, status=status.HTTP_400_BAD_REQUEST)
            constat.rejeter(commentaire)
            message = 'Constat rejeté.'
        else:
            return Response({'detail': 'Action invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'detail': message,
            'id': constat.id,
            'statut': constat.statut,
            'commentaire_admin': constat.commentaire_admin
        }, status=status.HTTP_200_OK)


class ConstatsParStatutView(generics.ListAPIView):
    """
    GET /api/constats/statut/<statut>/ — liste des constats par statut (admin seulement)
    """
    serializer_class = ConstatSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        statut = self.kwargs['statut']
        return Constat.objects.filter(statut=statut).order_by('-date_creation')
    
class RecevoirPDFView(APIView):
    """POST /api/constats/<id>/recevoir-pdf/ — reçoit le PDF généré côté frontend"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            constat = Constat.objects.get(pk=pk)
        except Constat.DoesNotExist:
            return Response({'detail': 'Constat introuvable.'}, status=404)

        if not request.user.is_admin and constat.technicien != request.user:
            return Response({'detail': 'Non autorisé.'}, status=403)

        if 'pdf_file' in request.FILES:
            constat.pdf_file = request.FILES['pdf_file']
            constat.save()

        return Response({
            'detail': 'PDF reçu.',
            'pdf_url': request.build_absolute_uri(constat.pdf_file.url) if constat.pdf_file else None
        })
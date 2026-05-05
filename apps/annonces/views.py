from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Annonce, LectureAnnonce
from .serializers import AnnonceSerializer, LectureAnnonceSerializer
from apps.accounts.permissions import IsAdmin


class ListCreateAnnonceView(generics.ListCreateAPIView):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer

    def get_permissions(self):
        return [IsAdmin()] if self.request.method == 'POST' else [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(envoyee_par=self.request.user)


class DerniereAnnonceView(APIView):
    """GET /api/annonces/derniere/ — la dernière annonce pour l'app mobile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        annonce = Annonce.objects.first()
        if not annonce:
            return Response({'message': None})
        deja_lue = LectureAnnonce.objects.filter(
            annonce=annonce, technicien=request.user
        ).exists()
        return Response({
            'id': annonce.id,
            'message': annonce.message,
            'date_envoi': annonce.date_envoi,
            'deja_lue': deja_lue
        })


class MarquerLueView(APIView):
    """POST /api/annonces/<id>/lue/ — technicien confirme lecture"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            annonce = Annonce.objects.get(pk=pk)
        except Annonce.DoesNotExist:
            return Response({'detail': 'Introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        LectureAnnonce.objects.get_or_create(
            annonce=annonce,
            technicien=request.user
        )
        return Response({'detail': 'Annonce marquée comme lue.'})
    
# Annonces privées
from .models import AnnoncePrivee
from .serializers import AnnoncePriveeSerializer


class AnnoncePriveeListCreateView(generics.ListCreateAPIView):
    """GET /api/annonces/privee/ — liste des messages privés
       POST /api/annonces/privee/ — envoyer un message privé (admin uniquement)"""
    serializer_class = AnnoncePriveeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return AnnoncePrivee.objects.all().order_by('-date_envoi')
        return AnnoncePrivee.objects.filter(destinataire=user).order_by('-date_envoi')

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)


class MarquerAnnoncePriveeLueView(APIView):
    """POST /api/annonces/privee/<id>/lue/ — technicien marque comme lu"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            annonce = AnnoncePrivee.objects.get(pk=pk)
        except AnnoncePrivee.DoesNotExist:
            return Response({'detail': 'Message privé introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Seul le destinataire peut marquer comme lu
        if annonce.destinataire != request.user:
            return Response({'detail': 'Vous n\'êtes pas le destinataire de ce message.'}, 
                          status=status.HTTP_403_FORBIDDEN)

        annonce.lu = True
        annonce.date_lecture = timezone.now()
        annonce.save()
        return Response({'detail': 'Message privé marqué comme lu.'})
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, RechargeGasoil
from .serializers import (
    UserSerializer, CreateUserSerializer, ChangePasswordSerializer,
    UpdateUserSerializer, RechargeGasoilSerializer
)
from .permissions import IsAdmin


class MeView(APIView):
    """GET/PATCH /api/auth/me/ — profil de l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ListCreateUserView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('last_name')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateUserSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.est_actif = False
        user.is_active = False
        user.save()
        return Response({'detail': 'Compte désactivé.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['ancien_mot_de_passe']):
            return Response({'detail': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['nouveau_mot_de_passe'])
        user.save()
        return Response({'detail': 'Mot de passe mis à jour.'})


class AdminChangePasswordView(APIView):
    """POST /api/auth/users/<id>/reset-password/"""
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        nouveau = request.data.get('nouveau_mot_de_passe')
        if not nouveau or len(nouveau) < 8:
            return Response({'detail': 'Mot de passe trop court (8 caractères min).'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(nouveau)
        user.save()
        return Response({'detail': f'Mot de passe de {user.username} mis à jour.'})


class RechargeGasoilViewSet(viewsets.ModelViewSet):
    """
    ✅ CRUD complet pour /api/gasoil/
    - Technicien : voit et crée ses propres recharges
    - Admin : voit toutes les recharges
    """
    serializer_class = RechargeGasoilSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return RechargeGasoil.objects.all().select_related('technicien')
        return RechargeGasoil.objects.filter(technicien=user).select_related('technicien')

    def perform_create(self, serializer):
        serializer.save(technicien=self.request.user)
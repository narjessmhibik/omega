from rest_framework import serializers
from .models import User, RechargeGasoil


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # ✅ CORRIGÉ : gasoil_mensuel (pas "gasoil")
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'role', 'telephone', 'est_actif', 'matricule_voiture', 'gasoil_mensuel','lien_drive' 
        ]
        read_only_fields = ['id']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password',
            'role', 'telephone', 'matricule_voiture', 'gasoil_mensuel','lien_drive' 
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'telephone',
            'role', 'est_actif', 'is_active', 'matricule_voiture', 'gasoil_mensuel','lien_drive' 
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    ancien_mot_de_passe = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, min_length=8)


class RechargeGasoilSerializer(serializers.ModelSerializer):
    technicien_nom = serializers.SerializerMethodField()

    class Meta:
        model = RechargeGasoil
        fields = ['id', 'technicien', 'technicien_nom', 'date', 'montant', 'kilometrage', 'created_at']
        read_only_fields = ['technicien', 'created_at']

    def get_technicien_nom(self, obj):
        return f"{obj.technicien.first_name} {obj.technicien.last_name}".strip() or obj.technicien.username
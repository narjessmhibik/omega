from rest_framework import serializers
from .models import (
    Intervention, Operateur, TypeIntervention,
    StatutIntervention, BaremeTechnicien, BaremeOperateur
)


class OperateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operateur
        fields = ['id', 'nom']


class TypeInterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeIntervention
        fields = ['id', 'nom']


class StatutInterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatutIntervention
        fields = ['id', 'nom']


class BaremeTechnicienSerializer(serializers.ModelSerializer):
    type_nom = serializers.SerializerMethodField()

    class Meta:
        model = BaremeTechnicien
        fields = ['id', 'type_intervention', 'type_nom', 'prix']

    def get_type_nom(self, obj):
        return obj.type_intervention.nom


class BaremeOperateurSerializer(serializers.ModelSerializer):
    type_nom = serializers.SerializerMethodField()
    operateur_nom = serializers.SerializerMethodField()

    class Meta:
        model = BaremeOperateur
        fields = ['id', 'type_intervention', 'type_nom', 'operateur', 'operateur_nom', 'prix']

    def get_type_nom(self, obj):
        return obj.type_intervention.nom

    def get_operateur_nom(self, obj):
        return obj.operateur.nom


class InterventionSerializer(serializers.ModelSerializer):
    est_modifiable = serializers.ReadOnlyField()
    gain_technicien = serializers.ReadOnlyField()
    ca_client = serializers.ReadOnlyField()
    marge = serializers.ReadOnlyField()
    technicien_nom = serializers.SerializerMethodField()
    operateur_nom = serializers.SerializerMethodField()
    type_nom = serializers.SerializerMethodField()
    statut_nom = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = [
            'id', 'technicien', 'technicien_nom',
            'ticket_id', 'operateur', 'operateur_nom',
            'type_intervention', 'type_nom',
            'statut', 'statut_nom',
            'adresse', 'ville', 'latitude', 'longitude',
            'date_intervention', 'date_creation', 'commentaire',
            'est_modifiable', 'gain_technicien', 'ca_client', 'marge'
        ]
        read_only_fields = ['id', 'date_creation', 'technicien']

    def get_technicien_nom(self, obj):
        return obj.technicien.get_full_name() or obj.technicien.username

    def get_operateur_nom(self, obj):
        return obj.operateur.nom if obj.operateur else '—'

    def get_type_nom(self, obj):
        return obj.type_intervention.nom if obj.type_intervention else '—'

    def get_statut_nom(self, obj):
        return obj.statut.nom if obj.statut else '—'


class CreateInterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = [
            'ticket_id', 'operateur', 'type_intervention',
            'statut', 'adresse', 'ville',
            'latitude', 'longitude',
            'date_intervention', 'commentaire'
        ]

    def create(self, validated_data):
        validated_data['technicien'] = self.context['request'].user
        return super().create(validated_data)
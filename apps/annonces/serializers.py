from rest_framework import serializers
from .models import Annonce, LectureAnnonce, AnnoncePrivee
from rest_framework import serializers


class AnnonceSerializer(serializers.ModelSerializer):
    nb_lectures = serializers.SerializerMethodField()

    class Meta:
        model = Annonce
        fields = ['id', 'message', 'date_envoi', 'envoyee_par', 'nb_lectures']
        read_only_fields = ['id', 'date_envoi', 'envoyee_par']

    def get_nb_lectures(self, obj):
        return obj.lectures.count()


class LectureAnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureAnnonce
        fields = ['id', 'annonce', 'technicien', 'date_lecture']
        read_only_fields = ['id', 'date_lecture', 'technicien']

class AnnoncePriveeSerializer(serializers.ModelSerializer):
    expediteur_nom = serializers.SerializerMethodField()
    destinataire_nom = serializers.SerializerMethodField()

    class Meta:
        model = AnnoncePrivee
        fields = ['id', 'expediteur', 'expediteur_nom', 'destinataire', 'destinataire_nom', 
                  'message', 'date_envoi', 'lu', 'date_lecture']
        read_only_fields = ['expediteur', 'date_envoi', 'lu', 'date_lecture']

    def get_expediteur_nom(self, obj):
        return f"{obj.expediteur.first_name} {obj.expediteur.last_name}".strip() or obj.expediteur.username

    def get_destinataire_nom(self, obj):
        return f"{obj.destinataire.first_name} {obj.destinataire.last_name}".strip() or obj.destinataire.username
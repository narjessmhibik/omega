# apps/constats/serializers.py
from rest_framework import serializers
from .models import Constat, PhotoConstat


class PhotoConstatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoConstat
        fields = ['id', 'photo', 'type_photo', 'latitude', 'longitude', 'horodatage_photo']


class ConstatSerializer(serializers.ModelSerializer):
    technicien_nom = serializers.SerializerMethodField()
    photos_avant = serializers.SerializerMethodField()
    photos_apres = serializers.SerializerMethodField()
    nb_photos = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Constat
        fields = [
            'id', 'intervention', 'technicien', 'technicien_nom',
            'categorie', 'description', 'photo', 'latitude', 'longitude',
            'signature', 'nom_signataire', 'date_signature',
            'date_creation', 'est_signe', 'pdf_file', 'pdf_url',
            'statut', 'date_soumission', 'commentaire_admin',
            'photos_avant', 'photos_apres', 'nb_photos'
        ]

    def get_technicien_nom(self, obj):
        if obj.technicien:
            return obj.technicien.get_full_name() or obj.technicien.username
        return None

    def get_photos_avant(self, obj):
        photos = obj.photos.filter(type_photo='avant')
        return PhotoConstatSerializer(photos, many=True).data

    def get_photos_apres(self, obj):
        photos = obj.photos.filter(type_photo='apres')
        return PhotoConstatSerializer(photos, many=True).data

    def get_nb_photos(self, obj):
        return obj.photos.count()
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None


class CreateConstatSerializer(serializers.ModelSerializer):
    photos_avant = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    photos_apres = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    pdf_file = serializers.FileField(required=False)

    class Meta:
        model = Constat
        fields = [
            'intervention', 'categorie', 'description',
            'photo', 'latitude', 'longitude',
            'photos_avant', 'photos_apres', 'pdf_file'
        ]
        extra_kwargs = {
            'intervention': {'required': False, 'allow_null': True},
            'photo': {'required': False},
            'latitude': {'required': False},
            'longitude': {'required': False},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        photos_avant = validated_data.pop('photos_avant', [])
        photos_apres = validated_data.pop('photos_apres', [])
        
        if request and request.user:
            validated_data['technicien'] = request.user
        
        constat = super().create(validated_data)
        
        # Ajouter les photos AVANT
        for photo in photos_avant:
            PhotoConstat.objects.create(
                constat=constat,
                photo=photo,
                type_photo='avant'
            )
        
        # Ajouter les photos APRÈS
        for photo in photos_apres:
            PhotoConstat.objects.create(
                constat=constat,
                photo=photo,
                type_photo='apres'
            )
        
        return constat


class SignatureSerializer(serializers.Serializer):
    """Pour enregistrer la signature du client"""
    nom_signataire = serializers.CharField(max_length=100)
    signature = serializers.ImageField()


class SoumettreConstatSerializer(serializers.Serializer):
    """Pour soumettre le constat à l'admin"""
    constat_id = serializers.IntegerField()


class ValiderConstatSerializer(serializers.Serializer):
    """Pour valider/rejeter le constat par l'admin"""
    action = serializers.ChoiceField(choices=['valider', 'rejeter'])
    commentaire = serializers.CharField(required=False, allow_blank=True)
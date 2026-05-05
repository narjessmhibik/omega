# apps/constats/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Constat(models.Model):
    CATEGORIE_CHOICES = [
        ('litige_client', 'Litige client'),
        ('litige_operateur', 'Litige opérateur'),
        ('probleme_materiel', 'Problème matériel'),
        ('incident_terrain', 'Incident terrain'),
        ('client_absent', 'Client absent'),
        ('acces_refuse', 'Accès refusé'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('soumis', 'Soumis'),
        ('valide', 'Validé par admin'),
        ('rejete', 'Rejeté'),
    ]
    
    intervention = models.ForeignKey('interventions.Intervention', on_delete=models.SET_NULL, null=True, blank=True)
    technicien = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    description = models.TextField(blank=True)
    
    # Photo unique (gardé pour compatibilité)
    photo = models.ImageField(upload_to='constats/', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    horodatage_photo = models.DateTimeField(null=True, blank=True)
    
    # Signature
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    nom_signataire = models.CharField(max_length=100, blank=True)
    date_signature = models.DateTimeField(null=True, blank=True)
    est_signe = models.BooleanField(default=False)
    
    # PDF généré
    pdf_file = models.FileField(upload_to='constats_pdf/', null=True, blank=True)
    
    # Statut et suivi
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_soumission = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Constat #{self.id} - {self.categorie} - {self.get_statut_display()}"
    
    def signer(self, nom_signataire, signature):
        self.nom_signataire = nom_signataire
        self.signature = signature
        self.date_signature = timezone.now()
        self.est_signe = True
        self.save()
    
    def soumettre(self):
        """Soumet le constat à l'admin"""
        self.statut = 'soumis'
        self.date_soumission = timezone.now()
        self.save()
    
    def valider(self, commentaire=None):
        """Valide le constat par l'admin"""
        self.statut = 'valide'
        if commentaire:
            self.commentaire_admin = commentaire
        self.save()
    
    def rejeter(self, commentaire):
        """Rejette le constat par l'admin"""
        self.statut = 'rejete'
        self.commentaire_admin = commentaire
        self.save()


class PhotoConstat(models.Model):
    """Modèle pour gérer plusieurs photos par constat"""
    TYPE_PHOTO = [
        ('avant', 'Avant intervention'),
        ('apres', 'Après intervention'),
    ]
    
    constat = models.ForeignKey(Constat, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='constats_photos/')
    type_photo = models.CharField(max_length=10, choices=TYPE_PHOTO)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    horodatage_photo = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo {self.type_photo} - Constat #{self.constat.id}"
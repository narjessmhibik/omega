from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User


class Operateur(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = 'Opérateur'


class TypeIntervention(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = "Type d'intervention"


class StatutIntervention(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = "Statut"


class BaremeTechnicien(models.Model):
    """Ce qu'on paye au technicien"""
    type_intervention = models.OneToOneField(
        TypeIntervention, on_delete=models.CASCADE, related_name='bareme_technicien'
    )
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.type_intervention.nom} → {self.prix} €"

    class Meta:
        verbose_name = 'Barème technicien'


class BaremeOperateur(models.Model):
    """Ce que l'opérateur nous paye"""
    type_intervention = models.ForeignKey(
        TypeIntervention, on_delete=models.CASCADE, related_name='baremes_operateurs'
    )
    operateur = models.ForeignKey(
        Operateur, on_delete=models.CASCADE, related_name='baremes'
    )
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        unique_together = ('type_intervention', 'operateur')
        verbose_name = 'Barème opérateur'

    def __str__(self):
        return f"{self.type_intervention.nom} / {self.operateur.nom} → {self.prix} €"


class Intervention(models.Model):
    technicien = models.ForeignKey(User, on_delete=models.PROTECT, related_name='interventions')
    ticket_id = models.CharField(max_length=100, blank=True)
    operateur = models.ForeignKey(Operateur, on_delete=models.SET_NULL, null=True, blank=True)
    type_intervention = models.ForeignKey(TypeIntervention, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.ForeignKey(StatutIntervention, on_delete=models.SET_NULL, null=True, blank=True)

    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    date_intervention = models.DateTimeField(default=timezone.now)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    commentaire = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_intervention']

    def __str__(self):
        return f"#{self.ticket_id} — {self.technicien} — {self.statut}"

    @property
    def est_modifiable(self):
        return timezone.now() < self.date_creation + timedelta(hours=24)

    @property
    def gain_technicien(self):
        try:
            if self.statut and self.statut.nom.lower() in ['réussie', 'reussie', 'réussi', 'reussi']:
                return self.type_intervention.bareme_technicien.prix
            return 0
        except Exception:
            return 0

    @property
    def ca_client(self):
        try:
            bareme = BaremeOperateur.objects.get(
                type_intervention=self.type_intervention,
                operateur=self.operateur
            )
            return bareme.prix
        except Exception:
            return 0

    @property
    def marge(self):
        return self.ca_client - self.gain_technicien
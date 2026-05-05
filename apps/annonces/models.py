from django.db import models
from apps.accounts.models import User


class Annonce(models.Model):
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    envoyee_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Annonce {self.id} — {self.date_envoi.strftime('%d/%m/%Y')}"


class LectureAnnonce(models.Model):
    """Trace quand un technicien a lu l'annonce"""
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='lectures')
    technicien = models.ForeignKey(User, on_delete=models.CASCADE)
    date_lecture = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('annonce', 'technicien')


# AJOUTE CE MODÈLE ICI
class AnnoncePrivee(models.Model):
    """Messages privés d'un admin vers un technicien spécifique"""
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, 
                                   related_name='annonces_envoyees')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='annonces_recues')
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Message privé #{self.id} — {self.expediteur.username} → {self.destinataire.username}"
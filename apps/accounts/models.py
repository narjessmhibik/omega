from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    TECHNICIEN = 'technicien'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (TECHNICIEN, 'Technicien'),
        (ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=TECHNICIEN)
    telephone = models.CharField(max_length=20, blank=True)
    est_actif = models.BooleanField(default=True)
    matricule_voiture = models.CharField(max_length=50, blank=True, null=True, verbose_name="Matricule voiture")
    gasoil_mensuel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Gasoil mensuel")
    lien_drive = models.URLField(max_length=500, blank=True, null=True, verbose_name="Lien Google Drive")
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_technicien(self):
        return self.role == self.TECHNICIEN


# ✅ Une seule définition de RechargeGasoil
class RechargeGasoil(models.Model):
    technicien = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recharges')
    date = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    kilometrage = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.technicien.username} - {self.date} - {self.montant}€"
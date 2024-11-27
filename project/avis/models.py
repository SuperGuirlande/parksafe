from django.db import models
from accounts.models import CustomUser
from reservations.models import Reservation


class AvisClientParker(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name="avis")
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='avis_donnes')
    parker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='avis_recus')

    avis = models.TextField(verbose_name="Avis")
    stars = models.IntegerField(verbose_name="Étoiles", default=5)

    created_on = models.DateField(auto_now=True, verbose_name="Reçu le")

    def __str__(self):
        if self.client:
            client_name = f"{self.client.first_name} {self.client.last_name[0]}."
        else:
            client_name = ("Profil supprimé")
        
        parker_name = f"{self.parker.first_name} {self.parker.last_name[0]}."

        return f"Avis de {client_name} vers {parker_name} | {self.stars}/5 étoiles"
    

class AvisResponse(models.Model):
    avis = models.ForeignKey(AvisClientParker, on_delete=models.CASCADE, blank=True, null=True, related_name="reponse", verbose_name="Avis")
    reponse = models.TextField(verbose_name="Réponse")

    def __str__(self):
        return self.reponse
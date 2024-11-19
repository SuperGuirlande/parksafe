from django.db import models
from accounts.models import CustomUser

class AvisClientParker(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='avis_donne')
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
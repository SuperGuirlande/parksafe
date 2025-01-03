from django.db import models



class ContactMessage(models.Model):
    first_name = models.CharField(verbose_name="Prénom", max_length=255)
    last_name = models.CharField(verbose_name="Nom", max_length=255)
    phone = models.CharField(verbose_name="Numéro de téléphone", max_length=16)
    email = models.EmailField(verbose_name="Adresse e-mail")
    message = models.TextField(verbose_name="Message")

    def __str__(self):
        return f"{self.first_name} {self.last_name} | {self.email} | {self.phone}"

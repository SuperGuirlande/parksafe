from django.db import models
from accounts.models import CustomUser
from parking_places.models import ParkingPlace
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField

class Reservation(models.Model):
    class VehiculeTypeChoice(models.TextChoices):
        VOITURE = 'VT', 'Voiture'
        UTILITAIRE = 'UT', 'Utilitaire'
        FOURGON = 'FG', 'Fourgon'
        CAMION = 'CM', 'Camion'
        VAN = 'VN', 'Van'
        CAMPING_CAR = 'CC', 'Camping Car'
        MOTO = 'MT', 'Moto'

    class VehiculesNumberChoice(models.IntegerChoices):
        ONE = 1, "1"
        TWO = 2, "2"
        THREE = 3, "3"
        FOUR = 4, "4"
        FIVE = 5, "5"


    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                               related_name="reservations", verbose_name="Client")
    parker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                               related_name="demandes", verbose_name="Hôte")
    place = models.ForeignKey(ParkingPlace, on_delete=models.SET_NULL, null=True,
                              related_name="reservations", verbose_name="Place de parking")
    token = models.CharField(max_length=16, verbose_name="Token d'identification", unique=True)

    days = models.IntegerField(verbose_name="Durée en jours", null=True, blank=True)
    price = models.DecimalField(verbose_name="Prix de l'hôte (en €)", max_digits=5, decimal_places=2, blank=True, null=True)
    commission = models.IntegerField(verbose_name="Commission ParkSafe", default=20)
    total_price = models.DecimalField(verbose_name="Prix de total (en €)", max_digits=5, decimal_places=2, blank=True, null=True)

    accepted = models.BooleanField(default=False, verbose_name="Acceptée par le loueur")
    payed = models.BooleanField(default=False, verbose_name="Payée par le client")
    finished = models.BooleanField(default=False, verbose_name="Réservation terminée")
    canceled = models.BooleanField(default=False, verbose_name="Réservation annulée")

    arrivee = models.DateTimeField(verbose_name="Date & Heure d'arrivée")
    departure = models.DateTimeField(verbose_name="Date & Heure de retour")
    
    vehicules_number = models.IntegerField(
        verbose_name="Nombre de véhicules",
        choices=VehiculesNumberChoice.choices,
        default=VehiculesNumberChoice.ONE, 

    )

    vehicule_type_1 = models.CharField(
        verbose_name="Type de véhicule",
        max_length=3,
        choices=VehiculeTypeChoice.choices,
        default=VehiculeTypeChoice.VOITURE
    ) 
    vehicule_type_2 = models.CharField(
        verbose_name="Type de véhicule",
        max_length=3,
        choices=VehiculeTypeChoice.choices,
        default=VehiculeTypeChoice.VOITURE
    ) 
    vehicule_type_3 = models.CharField(
        verbose_name="Type de véhicule",
        max_length=3,
        choices=VehiculeTypeChoice.choices,
        default=VehiculeTypeChoice.VOITURE
    ) 
    vehicule_type_4 = models.CharField(
        verbose_name="Type de véhicule",
        max_length=3,
        choices=VehiculeTypeChoice.choices,
        default=VehiculeTypeChoice.VOITURE
    ) 
    vehicule_type_5 = models.CharField(
        verbose_name="Type de véhicule",
        max_length=3,
        choices=VehiculeTypeChoice.choices,
        default=VehiculeTypeChoice.VOITURE
    ) 

    vehicule_model_1 = models.CharField(verbose_name="Marque / Modèle", max_length=255, blank=True, null=True)
    vehicule_model_2 = models.CharField(verbose_name="Marque / Modèle", max_length=255, blank=True, null=True)
    vehicule_model_3 = models.CharField(verbose_name="Marque / Modèle", max_length=255, blank=True, null=True)
    vehicule_model_4 = models.CharField(verbose_name="Marque / Modèle", max_length=255, blank=True, null=True)
    vehicule_model_5 = models.CharField(verbose_name="Marque / Modèle", max_length=255, blank=True, null=True)

    passengers=models.IntegerField(default=1, verbose_name="Nombre de passager(s)")
    phone = phone = PhoneNumberField(region='FR')
    message = models.TextField(verbose_name="Message")

    def save(self, *args, **kwargs):
        # GENERATE UNIQUE TOKEN
        if not self.token:
            test = get_random_string(length=16)
            while Reservation.objects.filter(token=test).exists():
                test = get_random_string(length=16)
            self.token = test
        # DAYS
        if not self.days:
            time = self.departure - self.arrivee
            self.days = time.days + 1
        # PRICE
        if not self.price:
            self.price = self.days * self.place.price

        if not self.total_price:
            self.total_price = self.price + (self.price * self.commission / 100)
        # SAVE
        super().save(*args, **kwargs)

    def __str__(self):
        formatted_arrivee = self.arrivee.strftime('%d/%m/%Y à %Hh%M')
        formatted_departure = self.departure.strftime('%d/%m/%Y à %Hh%M')
        return f"Réservation de {self.client.first_name} {self.client.last_name[0]}. vers {self.parker.first_name} {self.parker.last_name[0]}. | Début: {formatted_arrivee} -- Fin: {formatted_departure}"
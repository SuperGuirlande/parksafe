import requests
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser


class ParkingPlace(models.Model):
    class DistanceChoices(models.TextChoices):
        LESS_THAN_5 = 'LT5', 'Moins de 5 minutes à pied'
        FIVE_MINUTES = '5M', '5 minutes à pied'
        TEN_MINUTES = '10M', '10 minutes à pied'
        FIFTEEN_MINUTES = '15M', '15 minutes à pied'
        TWENTY_AND_MORE = '20M', '20 minutes à pied ou plus'

    class PlaceTypesChoices(models.TextChoices):
        CHEMIN_PRIVE = 'CP', 'Chemin privé'
        COURS_FERMEE = 'CF', 'Cour de maison fermée'
        COUR_OUVERTE = 'CO', 'Cour de maison ouverte'
        PLACE_PARKING = 'PP', 'Place de parking'
        GRAND_TERRAIN = 'TP', 'Grand terrain'

    class VehiculeAcceptedChoice(models.TextChoices):
        ALL_VEHICULES = 'ALL', 'Tous types de véhicules'
        VOITURE = 'VT', 'Voiture Citadine ou Familiale'
        MOTO = 'MT', 'Moto'
        CAMIONNETTE = 'UT', 'Camionnette ou Utilitaire'
        REMORQUE = "RM", "Véhicule avec Remorque ou Bateau"

    places = models.IntegerField(verbose_name="Nombre de places*", default=1)
    address = models.CharField(verbose_name="Adresse complète*", max_length=255)
    description = models.TextField(verbose_name="Description détaillée*")
    price = models.DecimalField(verbose_name="Prix journalier par véhicule* (en €)", max_digits=5, decimal_places=2)
    thumbnail = models.ImageField(verbose_name="Photo pour miniature", upload_to="places/thumbnail", default="places/thumbnail/default.png", blank=True, null=True)

    vehicles_types = models.CharField(
        verbose_name="Type(s) de véhicule(s) accepté(s)*",
        max_length=50,
    )   
    distance_to_transport = models.CharField(
        verbose_name="Distance à pied des transports en commun*",
        max_length=3,
        choices=DistanceChoices.choices,
        default=DistanceChoices.LESS_THAN_5
    )   


    navette_possible = models.BooleanField(verbose_name="J'éffectue le transport des voyageurs vers leur destination'*", default=False)
    navette_nocturne_possible = models.BooleanField(verbose_name="Je peux effectuer des navettes de nuit (entre 21h et 8h):*", default=False)

    navette_price = models.DecimalField(verbose_name="Prix d'une navette aller/retour:* (en €)", max_digits=5, decimal_places=2, default=0)
    navette_nocturne_price = models.DecimalField(verbose_name="Prix d'une navette de nuit aller/retour:* (en €)", max_digits=5, decimal_places=2, default=0)

    handicaped_place = models.BooleanField(verbose_name="J'ai au moins une place adaptée aux personnes à mobilité réduite", default=False)
    electric_vehicle = models.BooleanField(verbose_name="Je recharge éventuellement les voitures électriques des particuliers *", default=False)

    minimal_time = models.IntegerField(verbose_name="Durée minimum du séjour acceptée (en jours) *", default=1)

    phone = models.CharField(verbose_name="Numéro de téléphone*", max_length=16)

    token = models.CharField(verbose_name="Token unique", max_length=16, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="places_proposees", verbose_name="Utilisateur associé")

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    latitude = models.FloatField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Longitude", null=True, blank=True)

    def geocode(self):
        if not self.latitude or not self.longitude:
            api_key = settings.HERE_API_KEY
            address = self.address.replace(' ', '+')
            url = f"https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['items']:
                    position = data['items'][0]['position']
                    self.latitude = position['lat']
                    self.longitude = position['lng']
                    print(f"Geocoded coordinates: {self.latitude}, {self.longitude}")  # Debugging

    def save(self, *args, **kwargs):
        # GENERATE UNIQUE TOKEN
        if not self.token:
            test = get_random_string(length=16)

            while ParkingPlace.objects.filter(token=test).exists():
                test = get_random_string(length=16)
            self.token = test
        # GEOCODING
        if not self.latitude or not self.longitude:
            self.geocode()
        # SAVE
        super().save(*args, **kwargs)
    
    def get_vehicles_types_display_list(self):
        """Retourne la liste des labels pour chaque type de véhicule sélectionné"""
        if not self.vehicles_types:
            return []
        types = self.vehicles_types.split(',')
        return [dict(self.VehiculeAcceptedChoice.choices)[type_] for type_ in types]

    def get_vehicles_types_display(self):
        """Retourne une chaîne formatée avec tous les types de véhicules"""
        return ", ".join(self.get_vehicles_types_display_list())

    def __str__(self):
        return f"{self.places} places. {self.address} - User : {self.user}"
    


class DevenirHoteCommentCaMarcheItem(models.Model):
    ordre = models.IntegerField(verbose_name="Ordre dans la section")
    title = models.CharField(max_length=255, verbose_name="Titre de la section")
    content = models.TextField(verbose_name="Contenu textuel de la section")

    def __str__(self):
        return f"N°{self.ordre} - {self.title}"
    

class PourquoiDevenirHoteItem(models.Model):
    ordre = models.IntegerField(verbose_name="Ordre dans la section")
    title = models.CharField(max_length=255, verbose_name="Titre de la section")
    content = models.TextField(verbose_name="Contenu textuel de la section")

    def __str__(self):
        return f"N°{self.ordre} - {self.title}"
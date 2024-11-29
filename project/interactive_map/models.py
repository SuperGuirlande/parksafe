# models.py
import math
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from parking_places.models import ParkingPlace
import requests
from django.db.models import F
from django.db.models.functions import Power, Sqrt


class PoiCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom de la catégorie")

    def __str__(self):
        return self.name

class PoiCity(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom de la Ville")

    def __str__(self):
        return self.name

class PointOfInterest(models.Model):
    category = models.ForeignKey(to=PoiCategory, on_delete=models.CASCADE, related_name="pois", verbose_name="Point d'intérêt")
    city = models.ForeignKey(to=PoiCity, on_delete=models.CASCADE, related_name='pois', verbose_name='Ville associée')
    
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    address = models.CharField(verbose_name="Adresse complète", max_length=255)
    latitude = models.FloatField(verbose_name="Latitude", null=True, blank=True)  
    longitude = models.FloatField(verbose_name="Longitude", null=True, blank=True)

    commission = models.IntegerField(verbose_name="Commission ParkSafe", blank=True, default=20)

    def find_nearby_parkings(self, radius_km=2):
        lat_radius = radius_km / 111
        lon_radius = radius_km / (111 * math.cos(math.radians(self.latitude)))

        return ParkingPlace.objects.filter(
            latitude__range=(self.latitude - lat_radius, self.latitude + lat_radius),
            longitude__range=(self.longitude - lon_radius, self.longitude + lon_radius),
        ).order_by('id')  # ou tout autre ordre souhaité

    def __str__(self):
        return f"{self.category.name} de {self.city.name}"

    def geocode(self):
        """Géocode l'adresse en utilisant l'API HERE"""
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.category.name}-{self.city.name}")
            slug = base_slug
            counter = 1
            while PointOfInterest.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        if not self.latitude or not self.longitude:
            self.geocode()
            
        super().save(*args, **kwargs)

    @staticmethod
    def find_closest_to_coordinates(latitude, longitude):
        """
        Trouve le Point d'Intérêt le plus proche des coordonnées données
        """
        return (
            PointOfInterest.objects
            .filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
            .annotate(
                distance=Sqrt(
                    Power(111.0 * (F('latitude') - latitude), 2) +
                    Power(111.0 * (F('longitude') - longitude) * 0.7, 2)
                )
            )
            .order_by('distance')
            .first()
        )
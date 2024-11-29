from interactive_map.models import PoiCategory, PointOfInterest
from reservations.models import Reservation
from django.db.models import Prefetch


class GlobalContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            user = request.user
            # Préchargement optimisé des catégories avec leurs POIs et villes
            poi_cats = PoiCategory.objects.prefetch_related(
                Prefetch(
                    'pois',
                    queryset=PointOfInterest.objects.select_related('city').order_by('city__name')
                )
            ).all()

            if user.is_authenticated:
                parker_waiting_accept = Reservation.objects.filter(
                    parker=user, 
                    accepted=False, 
                    payed=False, 
                    finished=False, 
                    canceled=False
                )
                client_waiting_payement = Reservation.objects.filter(
                    client=user, 
                    accepted=True, 
                    payed=False, 
                    finished=False, 
                    canceled=False
                )
            
            # Traitement des catégories et villes avec slugs
            for cat in poi_cats:
                cities = []
                seen_cities = set()  # Pour éviter les doublons
                
                for poi in cat.pois.all():
                    city_name = poi.city.name
                    if city_name not in seen_cities:
                        cities.append({
                            'name': city_name,
                            'slug': poi.slug  # Le slug contient déjà la combinaison catégorie-ville
                        })
                        seen_cities.add(city_name)
                
                cat.unique_cities = cities
                cat.url_name = cat.name
            
            # Ajout au contexte
            response.context_data['poi_cats'] = poi_cats

            if user.is_authenticated:
                response.context_data['parker_waiting_accept'] = parker_waiting_accept
                response.context_data['client_waiting_payement'] = client_waiting_payement

        return response
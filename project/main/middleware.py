from interactive_map.models import PoiCategory
from reservations.models import Reservation


class GlobalContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            user=request.user
            poi_cats = PoiCategory.objects.all()

            if user.is_authenticated:
                parker_waiting_accept = Reservation.objects.filter(parker=user, accepted=False, payed=False, finished=False, canceled=False)
                client_waiting_payement = Reservation.objects.filter(client=user, accepted=True, payed=False, finished=False, canceled=False)
            
            for cat in poi_cats:
                cat.unique_cities = cat.pois.values_list('city__name', flat=True).distinct().order_by('city__name')
                cat.url_name = cat.name
            
            response.context_data['poi_cats'] = poi_cats

            if user.is_authenticated:
                response.context_data['parker_waiting_accept'] = parker_waiting_accept
                response.context_data['client_waiting_payement'] = client_waiting_payement

        return response
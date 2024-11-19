from interactive_map.models import PoiCategory

class GlobalContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            poi_cats = PoiCategory.objects.all()
            
            # Ajouter les villes uniques pour chaque catégorie
            for cat in poi_cats:
                cat.unique_cities = cat.pois.values_list('city__name', flat=True).distinct().order_by('city__name')
                # Ajouter le nom de la catégorie pour les URLs
                cat.url_name = cat.name
            
            response.context_data['poi_cats'] = poi_cats
            
        return response
from django import template
from parking_places.views import get_simple_format_adress
from avis.models import AvisClientParker


register = template.Library()

@register.filter
def simple_format_title(parking_place):
    return get_simple_format_adress(parking_place)

@register.filter
def get_rank(user):
    avis = AvisClientParker.objects.filter(parker=user)
    count = avis.count()
    total = 0
    for a in avis:
        total += a.stars
        print(a.stars)

    rank = total/count
    print(f"Nb avis: {count}")
    print(f"Total: {total}")
    print(f"Moyenne: {rank}")
    return rank
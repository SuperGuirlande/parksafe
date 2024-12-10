from django import template
from parking_places.views import get_simple_format_adress
from avis.models import AvisClientParker
from reservations.models import Reservation


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


@register.filter
def get_accept_rate(user):
    reservations = Reservation.objects.filter(parker=user)

    accepted = reservations.filter(accepted=True)
    refused = reservations.filter(refused=True)

    accepted_count = accepted.count()
    refused_count = refused.count()
    total_count = accepted_count + refused_count


    print(f"Réservations : {total_count}")
    print(f"Acceptées : {accepted_count}")

    if total_count == 0:
        return 0
    
    rate = (accepted_count / total_count) * 100
    print(f"Taux : {rate}")

    return round(rate, 2)


@register.filter
def remove_plural(value):
    if value.name.endswith('s'):
        return value.name[:-1]
    return value.name


@register.filter
def get_vehicule_type(reservation, index):
    return getattr(reservation, f'vehicule_type_{index}', None)

@register.filter
def attr(obj, attr_name):
    try:
        # Ne supprimez pas l'underscore final
        return getattr(obj, attr_name, None)
    except AttributeError:
        return None


@register.simple_tag
def range_vehicles(n):
    return range(1, n+1)
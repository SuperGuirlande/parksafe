import hashlib
import time
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from .forms import CreateParkingPlaceForm, IndisponibilityForm, SearchParkingForm
from .models import ParkingPlace
from interactive_map.models import PointOfInterest
from django.db.models import Q, F, Min
from django.db.models.functions import Power, Sqrt
from faq.models import FaqItem
from reservations.forms import ReservationForm
from .models import DevenirHoteCommentCaMarcheItem, PourquoiDevenirHoteItem
from datetime import datetime, timedelta
from django.db.models import F
from django.db.models.functions import Power, Sqrt
from django.db.models import Avg
from parking_places.models import CommentCaMarcheItem, PourquoiParksafeItem


def get_simple_format_adress(parking_place):
    user = parking_place.user
    name = f"{user.first_name} {user.last_name[0]}." 
    try:
        full_address = parking_place.address
        parts = full_address.split(',')
        
        postal_code = parts[1].strip().split()[0]  
        formatted_postal_code = f"{postal_code[:2]} {postal_code[2:]}"
        
        city = parts[1].strip().split()[1:]  
        city = ' '.join(city) 
        
        title = f"{city} ({formatted_postal_code})"

        return f"{title} - Chez {name}"
        
    except (IndexError, AttributeError):
        # Si erreur, on retourne l'adresse complète
        return f"{parking_place.address} - Chez {name}"


# DEVENIR HOTE PARKSAFE
def devenir_hote(request):
    ccm_items = DevenirHoteCommentCaMarcheItem.objects.all().order_by('ordre')
    pdh_items = PourquoiDevenirHoteItem.objects.all().order_by('ordre')

    return TemplateResponse(request, 'parking_places/devenir_hote.html', context={
        'ccm_items': ccm_items,
        'pdh_items': pdh_items,
    })

# CREER UNE PLACE DE PARKING
def create_parking_place(request):
    if not request.user.is_authenticated:
        return redirect('register')
    
    if request.method == 'POST':
        form = CreateParkingPlaceForm(request.POST, request.FILES)
        if form.is_valid():
            new_place = form.save(commit=False)
            new_place.user = request.user

            if request.user.is_superuser:
                new_place.admin_accepted = True
            else:
                from auto_messages.views import send_place_created_mail, send_place_created_sms
                # Send SMS notification
                success_parker, error_parker = send_place_created_sms(new_place)
                if not success_parker:
                    print(f"Erreur lors de l'envoi du SMS au propriétaire: {error_parker}")
                # Send EMAIL notification
                send_place_created_mail(new_place)

            new_place.save()
            return redirect('place_created_confirm')
    else:
        form = CreateParkingPlaceForm()

    context = {
        'form': form,
        'here_api_key': settings.HERE_API_KEY,
    }
    return TemplateResponse(request, 'parking_places/create_parking_place.html', context)


# MODIFIER UNE PLACE DE PARKING
def change_parking_place(request, token):
    if not request.user.is_authenticated:
        return redirect('register')
    
    place = get_object_or_404(ParkingPlace, token=token)

    if request.method == 'POST':
        form = CreateParkingPlaceForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            form.save()
            request.session['message'] = "Votre annonce a été modifiée avec succès !"
            return redirect('parker_index')
    else:
        form = CreateParkingPlaceForm(instance=place)

    context = {
        'place': place,
        'form': form,
        'here_api_key': settings.HERE_API_KEY,
    }
    return TemplateResponse(request, 'parking_places/change_parking_place.html', context)


# CONFIRMATION DE CREATION DE PLACE
def place_created_confirm(request):
    return TemplateResponse(request, 'parking_places/place_created.html', context={})


def update_url_params(base_url, params, key, value=None):
    """
    Helper pour mettre à jour les paramètres d'URL
    Si value est None, on bascule le booléen existant
    """
    new_params = params.copy()
    
    if value is None:
        # Pour les filtres booléens, on bascule la valeur
        current_value = params.get(key) == 'true'
        new_params[key] = str(not current_value).lower()
    else:
        # Pour le tri, on met simplement la nouvelle valeur
        new_params['sort'] = value
        
    return f"{base_url}?{new_params.urlencode()}"


def search_parking_place_index(request, poi_slug=None):
    # Récupérer les paramètres de tri et filtrage
    sort_by = request.GET.get('sort', '')  # Prix croissant par défaut
    handicap_filter = request.GET.get('handicap', '') == 'true'
    electric_filter = request.GET.get('electric', '') == 'true'
    navette_filter = request.GET.get('navette', '') == 'true'
    navette_nocturne_filter = request.GET.get('navette_nocturne', '') == 'true'
    ccm_items = CommentCaMarcheItem.objects.all().order_by('ordre')
    pq_items = PourquoiParksafeItem.objects.all().order_by('ordre') 


    # Base queryset
    if request.user.is_authenticated:
        all_places = ParkingPlace.objects.filter(
            admin_accepted=True, 
            deleted=False
        )
    else:
        all_places = ParkingPlace.objects.filter(
            admin_accepted=True, 
            deleted=False
        )

    radius_km = 20
    form = None
    poi = None
    commission = 20

    # Appliquer les filtres de base
    if handicap_filter:
        all_places = all_places.filter(handicaped_place=True)
    if electric_filter:
        all_places = all_places.filter(electric_vehicle=True)
    if navette_filter:
        all_places = all_places.filter(navette_possible=True)
    if navette_nocturne_filter:
        all_places = all_places.filter(navette_nocturne_possible=True)

    # Logique pour POI
    if poi_slug:
        poi = get_object_or_404(PointOfInterest, slug=poi_slug)
        commission = poi.commission
        
        # Calcul des places dans le rayon pour ce POI
        degree_radius = radius_km / 111
        lat_range = (poi.latitude - degree_radius, poi.latitude + degree_radius)
        lon_range = (poi.longitude - degree_radius, poi.longitude + degree_radius)
        
        all_places = all_places.filter(
            latitude__range=lat_range,
            longitude__range=lon_range,
            latitude__isnull=False,
            longitude__isnull=False
        ).annotate(
            distance=Sqrt(
                Power(111.0 * (F('latitude') - poi.latitude), 2) +
                Power(111.0 * (F('longitude') - poi.longitude) * 0.7, 2)
            )
        ).filter(distance__lte=radius_km)

    else:
        # Logique du formulaire
        if request.method == 'POST':
            form = SearchParkingForm(request.POST)
            if form.is_valid():
                poi = form.cleaned_data['point_of_interest']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                commission = poi.commission

                # Calcul des places dans le rayon
                degree_radius = radius_km / 111
                lat_range = (poi.latitude - degree_radius, poi.latitude + degree_radius)
                lon_range = (poi.longitude - degree_radius, poi.longitude + degree_radius)
                
                all_places = all_places.filter(
                    latitude__range=lat_range,
                    longitude__range=lon_range,
                    latitude__isnull=False,
                    longitude__isnull=False
                ).annotate(
                    distance=Sqrt(
                        Power(111.0 * (F('latitude') - poi.latitude), 2) +
                        Power(111.0 * (F('longitude') - poi.longitude) * 0.7, 2)
                    )
                ).filter(distance__lte=radius_km)

                # Filtrer les places indisponibles
                all_places = all_places.exclude(
                    indisponibilities__start_date__lte=end_date,
                    indisponibilities__end_date__gte=start_date
                )
        else:
            form = SearchParkingForm()

    # Appliquer le tri
    if sort_by == 'price_asc':
        all_places = all_places.order_by('price')
    elif sort_by == 'price_desc':
        all_places = all_places.order_by('-price')
    elif sort_by == 'rating':
        all_places = all_places.annotate(
            user_rating=Avg('user__avis_recus__stars')
        ).order_by('-user_rating')
    elif sort_by == 'distance' and poi:
        all_places = all_places.order_by('distance')
    else:
        all_places = all_places.order_by("-created_on")

    # Calculer le prix total avec la commission
    for place in all_places:
        place.total_price = place.price + (place.price * commission / 100)
        if hasattr(place, 'distance'):
            place.distance_km = round(place.distance, 2)
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # Construire l'URL de base pour les filtres
    base_url = request.path
    current_filters = request.GET.copy()
    
    # Préparer les URLs pour le template
    filter_urls = {
        'handicap': update_url_params(base_url, current_filters, 'handicap'),
        'electric': update_url_params(base_url, current_filters, 'electric'),
        'navette': update_url_params(base_url, current_filters, 'navette'),
        'navette_nocturne': update_url_params(base_url, current_filters, 'navette_nocturne'),
    }
    
    sort_urls = {
        'price_asc': update_url_params(base_url, current_filters, 'sort', 'price_asc'),
        'price_desc': update_url_params(base_url, current_filters, 'sort', 'price_desc'),
        'rating': update_url_params(base_url, current_filters, 'sort', 'rating'),
        'distance': update_url_params(base_url, current_filters, 'sort', 'distance'),
    }

    context = {
        'all_places': all_places[:10],
        'form': form,
        'poi': poi,
        'commission': commission,
        'radius_km': radius_km,
        'poi_cats': PointOfInterest.objects.values('category__name').distinct(),
        'today': today,
        'tomorrow': tomorrow,
        'current_sort': sort_by,
        'current_filters': {
            'handicap': handicap_filter,
            'electric': electric_filter,
            'navette': navette_filter,
            'navette_nocturne': navette_nocturne_filter,
        },
        'filter_urls': filter_urls,
        'sort_urls': sort_urls,
        'ccm_items': ccm_items,
        'pq_items': pq_items,
        }

    return TemplateResponse(request, "parking_places/found_place_index.html", context)


def parking_place_detail(request, token):
    place = get_object_or_404(ParkingPlace, token=token)
    faq_items = FaqItem.objects.all()
    avis_recus = place.user.avis_recus.all().order_by('-id')
    
    # Trouver le POI le plus proche et sa commission
    if place.latitude and place.longitude:
        closest_poi = PointOfInterest.find_closest_to_coordinates(place.latitude, place.longitude)
        commission = closest_poi.commission if closest_poi else 20
    else:
        commission = 20
    
    place.total_price = place.price + (place.price * commission / 100)
    
    context = {
        'place': place,
        'api_key': settings.HERE_API_KEY,
        'faq_items': faq_items,
        'avis_recus': avis_recus,
        'commission': commission,
        'closest_poi': closest_poi if 'closest_poi' in locals() else None,
    }
    return TemplateResponse(request, 'parking_places/place_detail.html', context)



# INDISPONIBILITE
def create_indisponibility(request):
    user = request.user

    if request.method == 'POST':
        form = IndisponibilityForm(user, request.POST)
        if form.is_valid():
            form.save()
            request.session['message'] = "La période d'indisponibilité à bien été ajoutée"
            return redirect('parker_index')
    else:
        form = IndisponibilityForm(user)

    context = {
        'form': form,
        'user': user,
    }

    return TemplateResponse(request, "parking_places/create_indisponibility.html", context)

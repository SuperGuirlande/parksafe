import hashlib
import time
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from .forms import CreateParkingPlaceForm
from .models import ParkingPlace
from interactive_map.models import PointOfInterest
from django.db.models import Q, F, Min
from django.db.models.functions import Power, Sqrt
from faq.models import FaqItem
from reservations.forms import ReservationForm
from .models import DevenirHoteCommentCaMarcheItem, PourquoiDevenirHoteItem


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
            return redirect('my_account_places')
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


def search_parking_place_index(request):
    all_places = ParkingPlace.objects.all().order_by("-created_on")
    
    poi_category = request.GET.get('category')
    poi_city = request.GET.get('city')
    radius_km = float(request.GET.get('radius', 20))
    
    if poi_category and poi_city:
        pois = PointOfInterest.objects.filter(
            category__name=poi_category,
            city__name=poi_city,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        if pois.exists():
            # On va calculer la distance pour chaque parking vers chaque POI
            parking_queries = Q()
            annotate_params = {}
            
            for i, poi in enumerate(pois):
                degree_radius = radius_km / 111
                lat_range = (poi.latitude - degree_radius, poi.latitude + degree_radius)
                lon_range = (poi.longitude - degree_radius, poi.longitude + degree_radius)
                
                # Filtre de base pour le rayon
                parking_queries |= Q(
                    latitude__range=lat_range,
                    longitude__range=lon_range
                )
                
                # Calcul de la distance pour ce POI
                distance_name = f'distance_{i}'
                annotate_params[distance_name] = Sqrt(
                    Power(111.0 * (F('latitude') - poi.latitude), 2) +
                    Power(111.0 * (F('longitude') - poi.longitude) * 0.7, 2)  # 0.7 est une approximation pour la France
                )
            
            # Filtrer et annoter les parkings avec leur distance minimale
            all_places = all_places.filter(
                parking_queries,
                latitude__isnull=False,
                longitude__isnull=False
            ).annotate(
                **annotate_params,  # Ajoute toutes les distances individuelles
                min_distance=Min(*annotate_params.keys())  # Trouve la distance minimale
            ).order_by('min_distance').distinct()
            
    context = {
        'all_places': all_places[:10],
        'selected_category': poi_category,
        'selected_city': poi_city,
        'search_radius': radius_km,
    }

    return TemplateResponse(request, "parking_places/found_place_index.html", context)


# DETAIL D'UNE PLACE
def parking_place_detail(request, token):
    place = get_object_or_404(ParkingPlace, token=token)
    faq_items = FaqItem.objects.all()
    avis_recus = place.user.avis_recus.all().order_by('-id')
    

    context = {
        'place': place,
        'api_key': settings.HERE_API_KEY,
        'faq_items': faq_items,
        'avis_recus': avis_recus,
    }
    return TemplateResponse(request, 'parking_places/place_detail.html', context)
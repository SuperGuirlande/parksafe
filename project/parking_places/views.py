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


def search_parking_place_index(request, poi_slug=None):
    if request.user.is_authenticated:
        all_places = ParkingPlace.objects.filter(admin_accepted=True, deleted=False).exclude(user=request.user).order_by("-created_on")
    else:
        all_places = ParkingPlace.objects.filter(admin_accepted=True, deleted=False).order_by("-created_on")

    radius_km = 15
    form = None
    poi = None
    commission = 20  # Commission par défaut

    if poi_slug:
        # Si on a un slug, on récupère directement le POI
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
        ).filter(distance__lte=radius_km).order_by('distance')

    else:
        # Sans slug, on utilise le formulaire
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
                ).filter(distance__lte=radius_km).order_by('distance')

                # Filtrer les places indisponibles pour les dates sélectionnées
                all_places = all_places.exclude(
                    indisponibilities__start_date__lte=end_date,
                    indisponibilities__end_date__gte=start_date
                )
        else:
            form = SearchParkingForm()

    # Calculer le prix total avec la commission
    for place in all_places:
        place.total_price = place.price + (place.price * commission / 100)
        if hasattr(place, 'distance'):
            place.distance_km = round(place.distance, 2)
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    context = {
        'all_places': all_places[:10],
        'form': form,
        'poi': poi,
        'commission': commission,
        'radius_km': radius_km,
        'poi_cats': PointOfInterest.objects.values('category__name').distinct(),
        'today': today,
        'tomorrow': tomorrow,
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

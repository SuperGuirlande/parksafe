from django.shortcuts import get_object_or_404, redirect, render
from .forms import AcceptMessageForm, ReservationForm
from .models import AcceptMessage, Reservation
from parking_places.models import ParkingPlace
from django.template.response import TemplateResponse
from interactive_map.models import PointOfInterest
from auto_messages.views import send_client_make_reserv_sms_to_client, send_client_make_reserv_sms_to_parker, send_client_make_reserv_email
from django.contrib.auth.decorators import login_required


@login_required
def make_reservation(request, place_token):
    
    place = get_object_or_404(ParkingPlace, token=place_token)
    hide_button = True
    
    # Find closest POI and commission
    if place.latitude and place.longitude:
        closest_poi = PointOfInterest.find_closest_to_coordinates(place.latitude, place.longitude)
        commission = closest_poi.commission if closest_poi else 20
    else:
        commission = 20
    
    place.total_price = place.price + (place.price * commission / 100)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reserv = form.save(commit=False)
            # Users & place
            reserv.client = request.user
            reserv.place = place
            reserv.parker = place.user
            # Total price   
            time = reserv.departure - reserv.arrivee
            reserv.days = time.days + 1
            
            # Calculate price with commission
            price = reserv.days * place.price
            reserv.price = price
            reserv.commission = commission
            reserv.total_price = price + (price * commission / 100)
            
            # Save
            reserv.save()

            # Send SMS notification
            success_parker, error_parker = send_client_make_reserv_sms_to_parker(reserv)
            success_client, error_client = send_client_make_reserv_sms_to_client(reserv)

            if not success_parker:
                print(f"Erreur lors de l'envoi du SMS au propriétaire: {error_parker}")
            if not success_client:
                print(f"Erreur lors de l'envoi du SMS au client: {error_client}")

            # Send EMAIL notification
            send_client_make_reserv_email(reserv)

            return redirect('reservation_confirm')
    else:
        form = ReservationForm()

    context = {
        'place': place,
        'hide_button': hide_button,
        'form': form,
        'commission': commission,
        'closest_poi': closest_poi if 'closest_poi' in locals() else None,
    }

    return TemplateResponse(request, 'reservations/make_reservation.html', context)


def reservation_confirm(request):
    return TemplateResponse(request, 'reservations/reservation_confirm.html', context={})

def accept_message(request, token):
    reservation = get_object_or_404(Reservation, token=token)

    if request.user != reservation.parker:
        return redirect('index')

    if request.method == 'POST':
        form = AcceptMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.reservation = reservation
            message.save()

            return redirect('parker_confirm_accept', token=reservation.token)
    else:
        form = AcceptMessageForm()

    return TemplateResponse(request, "reservations/accept_message_form.html", context={
        'form': form,
        'reservation': reservation,
    })


def reservation_detail(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    reponse = AcceptMessage.objects.filter(reservation=reservation).last()

    if reservation.parker == request.user:
        is_parker = True
    else:
        is_parker = False

    vehicles = [
        {
            'type': reservation.get_vehicle_type_display(getattr(reservation, f"vehicule_type_{i}", None)),
            'model': getattr(reservation, f"vehicule_model_{i}", None)
        }
        for i in range(1, reservation.vehicules_number + 1)
    ]

    context = {
        'reservation': reservation,
        'vehicles': vehicles,
        'reponse': reponse,
        'is_parker': is_parker,
    }

    return TemplateResponse(request, 'reservations/reservation_detail.html', context)
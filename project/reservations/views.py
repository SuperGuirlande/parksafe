from django.shortcuts import get_object_or_404, redirect, render
from .forms import AcceptMessageForm, ReservationForm
from .models import Reservation
from parking_places.models import ParkingPlace
from django.template.response import TemplateResponse


def make_reservation(request, place_token):
    place = get_object_or_404(ParkingPlace, token=place_token)
    hide_button = True
    place.total_price = place.price + ( place.price * 20 / 100 )

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
            reserv.price = reserv.days * place.price
            # Save
            reserv.save()
            return redirect('reservation_confirm')
    else:
        form = ReservationForm()

    context = {
        'place': place,
        'hide_button': hide_button,
        'form': form,
    }

    return TemplateResponse(request, 'reservations/make_reservation.html', context)

def reservation_confirm(request):
    return TemplateResponse(request, 'reservations/reservation_confirm.html', context={})

def accept_message(request, token):
    reservation = get_object_or_404(Reservation, token=token)

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
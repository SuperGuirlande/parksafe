from django.shortcuts import get_object_or_404, redirect, render
from .forms import ReservationForm
from .models import Reservation
from parking_places.models import ParkingPlace
from django.template.response import TemplateResponse


def make_reservation(request, place_token):
    place = get_object_or_404(ParkingPlace, token=place_token)
    hide_button = True

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reserv = form.save(commit=False)
            reserv.client = request.user
            reserv.place = place
            reserv.parker = place.user
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
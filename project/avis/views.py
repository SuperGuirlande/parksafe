from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from .models import AvisClientParker
from .forms import AvisClientParkerForm, AvisReponseForm
from parking_places.models import ParkingPlace
from reservations.models import Reservation


def new_avis_client_parker(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    parker = reservation.parker
    client = reservation.client

    if request.method == 'POST':
        form = AvisClientParkerForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.reservation = reservation
            avis.client = client
            avis.parker = parker
            avis.save()
            request.session['message'] = "Votre avis client à bien été posté !"
            return redirect('client_index')
        else:
            request.session['alert'] = "Il y à un soucis dans le formulaire"
    else:
        form = AvisClientParkerForm()


    return TemplateResponse(request, 'avis/avis_client_parker_form.html', context={
        'parker': parker,
        'client': client,
        'form': form,
        'reservation': reservation,
    })

def new_avis_reponse(request, id):
    avis = get_object_or_404(AvisClientParker, id=id)

    if request.method == 'POST':
        form = AvisReponseForm(request.POST)

        if form.is_valid():
            reponse = form.save(commit=False)
            reponse.avis = avis
            reponse.save()
            request.session['message'] = "Votre réponse à l'avis client à été envoyée avec succès"
            return redirect('parker_index')
    else:
        form = AvisReponseForm()

    context = {
        'form': form,
        'avis': avis,
    }            

    return TemplateResponse(request, "avis/avis_response_form.html", context)
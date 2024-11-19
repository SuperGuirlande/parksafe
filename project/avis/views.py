from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from .models import AvisClientParker
from .forms import AvisClientParkerForm
from parking_places.models import ParkingPlace

def new_avis_client_parker(request, token):
    place = get_object_or_404(ParkingPlace, token=token)
    parker = place.user
    client = request.user

    if request.method == 'POST':
        form = AvisClientParkerForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.client = client
            avis.parker = parker
            avis.save()
            request.session['message'] = "Votre avis client à bien été posté !"
            return redirect('my_account')
        else:
            request.session['alert'] = "Il y à un soucis dans le formulaire"
    else:
        form = AvisClientParkerForm()


    return TemplateResponse(request, 'avis/avis_client_parker_form.html', context={
        'parker': parker,
        'client': client,
        'form': form,
    })
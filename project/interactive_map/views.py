import hashlib
import time
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PointOfInterestForm, PoiCategoryForm, PoiCityForm, PoiCommissionForm
from interactive_map.models import PoiCategory, PoiCity, PointOfInterest
from django.template.response import TemplateResponse


# INDEX POI
@login_required
def poi_index(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    categories = PoiCategory.objects.all()
    cities = PoiCity.objects.all()
    pois = PointOfInterest.objects.all()

    context = {
        'categories': categories,
        'cities': cities,
        'pois': pois,
    }
    print(categories)
    return TemplateResponse(request, 'accounts/admin/poi/poi_index.html', context)


# CREATE POI CATEGORY
@login_required
def create_poi_category(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        form = PoiCategoryForm(request.POST)
        if form.is_valid:
            form.save()
            request.session['message'] = "La catégorie à bien été créée"
            return redirect('poi_index')
    else:
        form = PoiCategoryForm()

    context = {'form': form}

    return TemplateResponse(request, 'accounts/admin/poi/create_category.html', context)


# CREATE POI CITY
@login_required
def create_poi_city(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        form = PoiCityForm(request.POST)
        if form.is_valid:
            form.save()
            request.session['message'] = "La ville à été ajoutée avec succès"
            return redirect('poi_index')
    else:
        form = PoiCityForm()

    context = {'form': form}

    return TemplateResponse(request, 'accounts/admin/poi/create_city.html', context)
    

@login_required
def create_poi(request, id=None):
    if not request.user.is_superuser:
        return redirect('index')
    
    if id:
        poi = get_object_or_404(PointOfInterest, id=id)
    else:
        poi = None
    
    if request.method == 'POST':
        if poi:
            form = PointOfInterestForm(request.POST, instance=poi)
            if form.is_valid():
                form.save()
                request.session['message'] = "Le point d'intérêt à été modifié avec succès"
                return redirect('poi_index') 
        else:
            form = PointOfInterestForm(request.POST)
            if form.is_valid():
                form.save()
                request.session['message'] = "Le point d'intérêt à été ajouté avec succès"
                return redirect('poi_index') 
    else:
        if poi:
            form = PointOfInterestForm(instance=poi)
        else:
            form = PointOfInterestForm()
    
    context = {
        'form': form,
        'poi': poi,
        'here_api_key': settings.HERE_API_KEY,
    }
    if poi:
        return TemplateResponse(request, 'accounts/admin/poi/change_poi.html', context)
    else:
        return TemplateResponse(request, 'accounts/admin/poi/create_poi.html', context)


# UPDATE COMMISSION
def update_poi_commission(request, id):
    poi = get_object_or_404(PointOfInterest, id=id)

    if request.method == 'POST':
        form = PoiCommissionForm(request.POST, instance=poi)
        if form.is_valid():
            form.save()
            request.session['message'] = "La commission a été mise à jour avec succès."
            return redirect('commissions_index')
    else:
        form = PoiCommissionForm(instance=poi)

    context = {
        'form': form,
        'poi': poi,
    }

    return TemplateResponse(request, "accounts/admin/commissions/update_commission.html", context)
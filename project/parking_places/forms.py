from django import forms
from .models import ParkingPlace
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator


class CreateParkingPlaceForm(forms.ModelForm):
    vehicles_types = forms.MultipleChoiceField(
        choices=ParkingPlace.VehiculeAcceptedChoice.choices,
        widget=forms.CheckboxSelectMultiple,
        label="Type(s) de véhicule(s) accepté(s)*"
    )

    class Meta:
        model = ParkingPlace
        fields = ['places', 'address', 'description', 'price', 'thumbnail', 'vehicles_types',
                  'distance_to_transport', 'navette_possible', 'navette_nocturne_possible',
                  'navette_price',  'navette_nocturne_price', 'handicaped_place', 'electric_vehicle', 'minimal_time',
                  'phone']

    def clean_vehicles_types(self):
        """Convertit la liste en string avec séparateur"""
        return ','.join(self.cleaned_data['vehicles_types'])
        
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return ''.join(phone.split())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.vehicles_types:
            self.initial['vehicles_types'] = self.instance.vehicles_types.split(',')
        self.fields['phone'].widget.attrs['placeholder'] = '06 07 08 09 10'
        self.fields['address'].widget.attrs.update({
            'id': 'addressInput',
            'autocomplete': 'off',
            'placeholder': "5 rue de la gare, 17000, La Rochelle"
        })
        self.fields['description'].widget.attrs.update({
            'placeholder': "Bonjour,\nje vous propose un emplacement de deux places à 5 minutes à pieds de la Gare du Nord.\nPeux contenir tous types de véhicules."
        })
        self.fields['price'].widget.attrs.update({
            'placeholder': "8,50"
        })
        for field in self.fields.values():
            field.label = mark_safe(field.label)
        
# class SimpleSearchForm():
    
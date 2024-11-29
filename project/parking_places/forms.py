from django import forms
from .models import ParkingPlace, PlaceIndisponibility
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator
from interactive_map.models import PointOfInterest


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
        

class SearchParkingForm(forms.Form):
    point_of_interest = forms.ModelChoiceField(
        queryset=PointOfInterest.objects.all(),
        label="Point d'intérêt",
        empty_label="Sélectionnez un point d'intérêt"
    )
    start_date = forms.DateField(
        label="Date de début",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="Date de fin",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )

        return cleaned_data


class IndisponibilityForm(forms.ModelForm):
    place = forms.ModelChoiceField(
        queryset=None,
        label="Place de parking",
        empty_label=None
    )
    debut = forms.DateTimeField(
        widget=forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={
            "type": "datetime-local",
            'min': timezone.now().strftime("%Y-%m-%dT%H:%M")
        }),
        input_formats=["%Y-%m-%d %H:%M"],
        label="Indisponible à partir du"
    )
    fin = forms.DateTimeField(
        widget=forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={
            "type": "datetime-local",
            'min': timezone.now().strftime("%Y-%m-%dT%H:%M")
        }),
        input_formats=["%Y-%m-%d %H:%M"],
        label="Indisponible jusqu'au"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = ParkingPlace.objects.filter(user=user)
        # Modifie l'affichage des places dans le select
        queryset.model.__str__ = lambda self: self.address
        self.fields['place'].queryset = queryset

    class Meta:
        model=PlaceIndisponibility

        fields = [
            'place',
            'debut',
            'fin',
        ]

    def clean(self):
        cleaned_data = super().clean()
        debut = cleaned_data.get('debut')
        fin = cleaned_data.get('fin')

        if debut and fin and fin <= debut:
            self.add_error('fin', 
                "La date de fin doit être ultérieure à la date de début.")

        return cleaned_data
from django import forms
from .models import ParkingPlace
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator


class CreateParkingPlaceForm(forms.ModelForm):
    class Meta:
        model = ParkingPlace
        fields = ['places', 'address', 'description', 'price', 'thumbnail', 'vehicles_types',
                  'distance_to_transport', 'navette_possible', 'navette_nocturne_possible',
                  'navette_price',  'navette_nocturne_price', 'handicaped_place', 'electric_vehicle', 'minimal_time',
                  'phone']
        
    phone_regex = RegexValidator(
        regex=r'^(0[67](\s?\d{2}){4})$',
        message="Le numéro de téléphone doit être au format '06 06 06 06 06' ou '0606060606'."
    )
    phone = forms.CharField(label='Numéro de téléphone', validators=[phone_regex], max_length=14)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return ''.join(phone.split())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
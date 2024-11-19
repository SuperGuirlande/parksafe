from django import forms 
from .models import Reservation
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget, RegionalPhoneNumberWidget
from django.forms import TextInput, Select


class ReservationForm(forms.ModelForm):
    arrivee = forms.DateTimeField(
        widget=forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={
            "type": "datetime-local",
            'min': timezone.now().strftime("%Y-%m-%dT%H:%M")
        }),
        input_formats=["%Y-%m-%d %H:%M"],
        label="Date & Heure d'arrivée"
    )
    departure = forms.DateTimeField(
        widget=forms.DateTimeInput(format="%Y-%m-%d %H:%M", attrs={
            "type": "datetime-local",
            'min': timezone.now().strftime("%Y-%m-%dT%H:%M")
        }),
        input_formats=["%Y-%m-%d %H:%M"],
        label="Date & Heure de départ"
    )
    phone = PhoneNumberField(
        region="FR",
        label="N° de téléphone",
        widget=RegionalPhoneNumberWidget(
            region="FR",
            attrs={
                'class': 'phone-input',
                'placeholder': '6 05 04 03 02'
            }
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,  # ou le nombre de lignes que vous souhaitez
            'placeholder': "Ex: Bonjour, nous seront 2 adultes et 2 enfants. Notre vol est prévue pour 15h30."
        })
    )
    vehicule_model_1 = forms.CharField(
        required=True,
        label="Modèle",
        widget=forms.TextInput(attrs={
            'placeholder': "Renault Clio / Renault Master",  # ou le nombre de lignes que vous souhaitez
        })
    )
    vehicule_model_2 = forms.CharField(
        required=False,
        label="Modèle",
        widget=forms.TextInput(attrs={
            'placeholder': "Renault Clio / Renault Master",  # ou le nombre de lignes que vous souhaitez
        })
    )
    vehicule_model_3 = forms.CharField(
        required=False,
        label="Modèle",
        widget=forms.TextInput(attrs={
            'placeholder': "Renault Clio / Renault Master",  # ou le nombre de lignes que vous souhaitez
        })
    )
    vehicule_model_4 = forms.CharField(
        required=False,
        label="Modèle",
        widget=forms.TextInput(attrs={
            'placeholder': "Renault Clio / Renault Master",  # ou le nombre de lignes que vous souhaitez
        })
    )
    vehicule_model_5 = forms.CharField(
        required=False,
        label="Modèle",
        widget=forms.TextInput(attrs={
            'placeholder': "Renault Clio / Renault Master",  # ou le nombre de lignes que vous souhaitez
        })
    )
    vehicule_type_1 = forms.ChoiceField(
        required=True, 
        label="Type de véhicule",
        choices=Reservation.VehiculeTypeChoice.choices,
        widget=forms.Select(attrs={
            'class': 'votre-classe'  # optionnel
        })
    )
    vehicule_type_2 = forms.ChoiceField(
        required=False, 
        label="Type de véhicule",
        choices=Reservation.VehiculeTypeChoice.choices,
        widget=forms.Select(attrs={
            'class': 'votre-classe'  # optionnel
        })
    )
    vehicule_type_3 = forms.ChoiceField(
        required=False, 
        label="Type de véhicule",
        choices=Reservation.VehiculeTypeChoice.choices,
        widget=forms.Select(attrs={
            'class': 'votre-classe'  # optionnel
        })
    )
    vehicule_type_4 = forms.ChoiceField(
        required=False, 
        label="Type de véhicule",
        choices=Reservation.VehiculeTypeChoice.choices,
        widget=forms.Select(attrs={
            'class': 'votre-classe'  # optionnel
        })
    )
    vehicule_type_5 = forms.ChoiceField(
        required=False, 
        label="Type de véhicule",
        choices=Reservation.VehiculeTypeChoice.choices,
        widget=forms.Select(attrs={
            'class': 'votre-classe'  # optionnel
        })
    )

    class Meta:
        model=Reservation
        fields=[
            'arrivee',
            'departure',
            'vehicules_number',
            'vehicule_type_1',
            'vehicule_type_2',
            'vehicule_type_3',
            'vehicule_type_4',
            'vehicule_type_5',
            'vehicule_model_1',
            'vehicule_model_2',
            'vehicule_model_3',
            'vehicule_model_4',
            'vehicule_model_5',
            'passengers',
            'phone',
            'message',
        ]
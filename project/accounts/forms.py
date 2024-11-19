import re 
from datetime import date, datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': "Prénom",
                'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
            }
        )
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': "Nom de famille",
                'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
            }
        )
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder':'Adresse email',
                'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Mot de passe',
                'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirmation du mot de passe',
                'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
            }
        )
    )


    def calculate_min_date_for_adult():
        today = date.today()
        return date(today.year - 18, today.month, today.day).strftime('%Y-%m-%d')

    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'text',
            'placeholder': 'Date de naissance ( JJ/MM/AAAA )',
            'class': 'rounded-xl w-full px-4 py-2 border border-slate-500',
        }),
        error_messages={
            'required': 'La date de naissance est obligatoire',
            'invalid': 'Format de date invalide. Utilisez JJ/MM/AAAA'
        }
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'birth_date', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Adresse e-mail"), widget=forms.TextInput)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Adresse email'
        self.fields['password'].widget.attrs['placeholder'] = 'Mot de passe'
        self.fields['username'].widget.attrs['class'] = 'rounded-xl w-full px-4 py-2 border border-slate-500'
        self.fields['password'].widget.attrs['class'] = 'rounded-xl w-full px-4 py-2 border border-slate-500'

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())



class MobileNumberForm(forms.Form):
    phone_regex = RegexValidator(
        regex=r'^(0[67](\s?\d{2}){4})$',
        message="Le numéro de téléphone doit être au format '06 06 06 06 06' ou '0606060606'."
    )
    phone = forms.CharField(label=_('Numéro de téléphone'), validators=[phone_regex], max_length=14)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        print("La méthode clean_phone est appelée !")  # Pour démonstration
        return ''.join(phone.split())
    
    def __init__(self, *args, **kwargs):
        super(MobileNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['placeholder'] = '06 07 08 09 10'


class ProfilPicForm(forms.Form):
    profil_pic = forms.ImageField(label=_("Image de profil"), required=True)
from django import forms
from .models import AvisClientParker

class AvisClientParkerForm(forms.ModelForm):
    class Meta:
        model=AvisClientParker
        fields=['stars', 'avis']
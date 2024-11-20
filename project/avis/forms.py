from django import forms
from .models import AvisClientParker


class AvisClientParkerForm(forms.ModelForm):
    avis = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': "Laissez votre message"}
        )
    )
    
    class Meta:
        model = AvisClientParker
        fields = ['stars', 'avis']
from django import forms
from .models import FaqItem


class FaqItemForm(forms.ModelForm):
    class Meta:
        model=FaqItem
        fields=['question', 'reponse']
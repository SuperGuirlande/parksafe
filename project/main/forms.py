from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = [
            'first_name',
            'last_name',
            'phone',
            'email',
            'message'
        ]
    
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '5',
            }
        )
    )
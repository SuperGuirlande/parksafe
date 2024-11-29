# forms.py
from django import forms
from .models import PointOfInterest, PoiCategory, PoiCity


class PoiCityForm(forms.ModelForm):
    class Meta:
        model=PoiCity
        fields=['name']


class PoiCategoryForm(forms.ModelForm):
    class Meta:
        model=PoiCategory
        fields=['name']


class PointOfInterestForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = PointOfInterest
        fields = ['category', 'city', 'address', 'latitude', 'longitude']
        widgets = {
            'address': forms.TextInput(attrs={
                'id': 'addressInput',
                'autocomplete': 'off',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.update({
                    'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                })


class PoiCommissionForm(forms.ModelForm):
    class Meta:
        model = PointOfInterest
        fields = ['commission']
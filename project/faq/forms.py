from django import forms
from .models import FaqItem
from django_ckeditor_5.widgets import CKEditor5Widget


class FaqItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reponse"].required = False

    class Meta:
        model=FaqItem
        fields=['question', 'reponse']
        widgets = {
            "reponse": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }
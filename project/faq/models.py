from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

class FaqItem(models.Model):
    question= models.CharField(max_length=255, unique=True, verbose_name="Question")
    reponse = CKEditor5Field(verbose_name="Reponse", config_name='extends')
    ordre = models.IntegerField(verbose_name="Ordre")

    def __str__(self):
        return self.question

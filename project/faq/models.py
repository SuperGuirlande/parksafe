from django.db import models


class FaqItem(models.Model):
    question= models.CharField(max_length=255, unique=True, verbose_name="Question")
    reponse = models.TextField(verbose_name="Reponse")
    ordre = models.IntegerField(verbose_name="Ordre")

    def __str__(self):
        return self.question

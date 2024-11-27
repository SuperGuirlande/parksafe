from django.urls import path
from django.conf import urls
from .views import new_avis_client_parker, new_avis_reponse

urlpatterns = [
    path('ecrire-avis-client-parker/<str:token>/', new_avis_client_parker, name='new_avis_client_parker'),
    path('repondre-a-un-avis/<int:id>/', new_avis_reponse, name='new_avis_reponse')
]

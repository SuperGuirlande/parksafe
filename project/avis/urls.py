from django.urls import path
from django.conf import urls
from .views import new_avis_client_parker

urlpatterns = [
    path('ecrire-avis-client-parker/<str:token>/', new_avis_client_parker, name='new_avis_client_parker')
]

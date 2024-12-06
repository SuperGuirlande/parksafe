from django.urls import path
from .views import index, a_propos, mentions_legales, confidentitalite, cgv


urlpatterns = [
    path('', index, name='index'),
    path('a-propos-de-parksafe/', a_propos, name='a_propos'),
    path('mentions-legales/', mentions_legales, name='mentions_legales'),
    path('politique-de-confidentialite/', confidentitalite, name='confidentitalite'),
    path('conditions-generales/', cgv, name='cgv'),
]

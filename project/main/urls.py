from django.urls import path
from .views import index, a_propos, mentions_legales, confidentitalite, cgv, contact


urlpatterns = [
    path('', index, name='index'),
    path('a-propos-de-parksafe/', a_propos, name='a_propos'),
    path('contact/', contact, name='contact'),
    path('mentions-legales/', mentions_legales, name='mentions_legales'),
    path('politique-de-confidentialite/', confidentitalite, name='confidentitalite'),
    path('conditions-generales/', cgv, name='cgv'),
]

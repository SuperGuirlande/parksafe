from django.urls import path
from .views import index, a_propos


urlpatterns = [
    path('', index, name='index'),
    path('a-propos-de-parksafe/', a_propos, name='a_propos'),
]

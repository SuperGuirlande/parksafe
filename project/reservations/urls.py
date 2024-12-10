from django import urls
from django.urls import path
from .views import make_reservation, reservation_confirm, reservation_detail


urlpatterns = [
    path('demande-de-reservation/<str:place_token>/', make_reservation, name='make_reservation'),
    path('confirmation-de-la-reservation/', reservation_confirm, name='reservation_confirm'),
    path('details/<str:token>/', reservation_detail, name='reservation_detail'),
]
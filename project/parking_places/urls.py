from django.urls import path
from .views import create_parking_place, search_parking_place_index, parking_place_detail, place_created_confirm, change_parking_place
from .views import devenir_hote, create_indisponibility


urlpatterns = [
    path('devenir-hote-parksafe/', devenir_hote, name="devenir_hote"),
    path('proposer-une-place-de-parking/', create_parking_place, name="create_parking_place"),
    path('modifier-annonce/<str:token>/', change_parking_place, name="change_parking_place"),
    path('confirmation-de-creation/', place_created_confirm, name="place_created_confirm"),
    path('detail-de-la-place/<str:token>/', parking_place_detail, name="parking_place_detail"),
    path('ajouter-une-indisponibilite/', create_indisponibility, name="create_indisponibility"),

    path('rechercher-une-place-de-parking/', search_parking_place_index, name="search_parking_place_index"),
    path('rechercher-une-place-de-parking/<slug:poi_slug>/', search_parking_place_index, name="search_parking_place"),
]

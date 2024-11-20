from django.urls import path
from .views import change_password, register, user_login, user_logout, my_account, general_redirect, change_mobile_number
from .views import change_profil_pic, admin_index, faq_index, faq_item_form, my_account_places, client_reservations_waiting
from .views import client_cancel_reservation, client_confirm_cancel, client_reservations_waiting_paiement
from .views import parker_reservation_waiting, parker_cancel_reservation, parker_confirm_cancel, parker_accept_reservation, parker_confirm_accept
from .views import devenir_hote_index, parker_my_gains, client_current_reservations, parker_my_reservations, client_finished_reservations
from interactive_map.views import create_poi, create_poi_category, create_poi_city, poi_index
from faq.views import move_faq_item
from django.contrib.auth import views as auth_views
from accounts.views import devenir_hote_add_ccm, devenir_hote_add_pdh, devenir_hote_edit_ccm, devenir_hote_edit_pdh

urlpatterns = [
    path('', general_redirect, name="general_redirection"),
    path('s-inscrire/', register, name='register'),
    path('se-connecter/', user_login, name='login'),
    path('se-deconnecter/', user_logout, name='logout'),
    path('nouveau-mot-de-passe/', change_password, name="change_password"),

    # ACCOUNT
    path('mon-compte/', my_account, name='my_account'),

    # CLIENT
    path('reservations-en-attente/', client_reservations_waiting, name='client_reservations_waiting'),
    path('annuler-ma-reservation/<str:token>/', client_cancel_reservation, name='client_cancel_reservation'),
    path('confirmer-l-annulation/<str:token>/', client_confirm_cancel, name='client_confirm_cancel'),
    path('reservations-en-attente-de-paiement/', client_reservations_waiting_paiement, name='client_reservations_waiting_paiement'),
    path('reservations-en-cours/', client_current_reservations, name='client_current_reservations'),
    path('reservations-terminees/', client_finished_reservations, name='client_finished_reservations'),

    # HOTE
    path('mes-places/', my_account_places, name='my_account_places'),
    path('mes-reservations/', parker_my_reservations, name='parker_my_reservations'),
    path('reservations-a-traiter/', parker_reservation_waiting, name='parker_reservation_waiting'),
    path('refuser-la-reservation/<str:token>/', parker_cancel_reservation, name='parker_cancel_reservation'),
    path('confirmer-le-refus/<str:token>/', parker_confirm_cancel, name='parker_confirm_cancel'),
    path('accepter-la-reservation/<str:token>/', parker_accept_reservation, name='parker_accept_reservation'),
    path('confirmer-l-acceptation/<str:token>/', parker_confirm_accept, name='parker_confirm_accept'),
    path('mes-revenus/', parker_my_gains, name='parker_my_gains'),

    # PASSWORD RESET
    path('reinitialiser-mot-de-passe/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset/password_reset_form.html'), name="password_reset"),
    path('reinitialiser-mot-de-passe/envoye/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset/password_reset_done.html'), name="password_reset_done"),
    path('reinitialiser/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset/password_reset_confirm.html'), name="password_reset_confirm"),
    path('reinitialiser/termine/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset/password_reset_complete.html'), name="password_reset_complete"),

    # CHANGE INFORMATIONS
    path('ajouter-numero-de-telephone/', change_mobile_number, name="change_mobile_number"),
    path('changer-image-de-profil/', change_profil_pic, name="change_profil_pic"),

    # ADMIN
    path('administrateur/', admin_index, name="admin_index"),

    # POI
    path('administrateur/points-d-interet/', poi_index, name="poi_index"),
    path('administrateur/points-d-interet/creer_point/', create_poi, name="create_poi"),
    path('administrateur/points-d-interet/modifier_point/<int:id>/', create_poi, name="change_poi"),
    path('administrateur/points-d-interet/creer_categorie/', create_poi_category, name="create_poi_category"),
    path('administrateur/points-d-interet/creer_ville/', create_poi_city, name="create_poi_city"),

    # FAQ
    path('administrateur/faq/', faq_index, name="faq_index"),
    path('administrateur/faq/creer-item/', faq_item_form, name="create_faq_item"),
    path('administrateur/faq/modifier-item/<int:id>/', faq_item_form, name="change_faq_item"),

    # DEVENIR HOTE
    path('administrateur/devenir_hote/', devenir_hote_index, name="devenir_hote_index"),
    path('administrateur/devenir-hote/add/ccm/', devenir_hote_add_ccm, name="devenir_hote_add_ccm"),
    path('administrateur/devenir_hote/add/pdh/', devenir_hote_add_pdh, name="devenir_hote_add_pdh"),
    path('administrateur/devenir-hote/edit/ccm/<int:id>/', devenir_hote_edit_ccm, name="devenir_hote_edit_ccm"),
    path('administrateur/devenir_hote/edit/pdh/<int:id>/', devenir_hote_edit_pdh, name="devenir_hote_edit_pdh"),
]

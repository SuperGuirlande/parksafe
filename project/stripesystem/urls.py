from django.urls import path
from .views import create_stripe_account, complete_stripe_account, stripe_reauth, stripe_return, create_checkout_session, payment_cancel, payment_success, transfer_earnings


urlpatterns = [
    path('create-stripe-account/', create_stripe_account, name='create_stripe_account'),
    path('complete-stripe-account/', complete_stripe_account, name='complete_stripe_account'),
    path('reauth/<str:account_id>/', stripe_reauth, name='stripe_reauth'),
    path('return/<str:account_id>/', stripe_return, name='stripe_return'),
    path('create-checkout-session/<str:reservation_token>/', create_checkout_session, name='create_checkout_session'),
    path('payment-success/', payment_success, name='payment_success'),
    path('payment-cancel/', payment_cancel, name='payment_cancel'),
    path('transfer-earnings/', transfer_earnings, name='transfer_earnings'),
]

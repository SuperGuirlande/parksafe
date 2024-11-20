# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import StripeConnectAccount, ReservationPayement
import stripe
from django.conf import settings
from django.contrib import messages
from reservations.models import Reservation


@login_required
def create_stripe_account(request):
    try:
        stripe_account, created = StripeConnectAccount.objects.get_or_create(
            user=request.user,
            defaults={'account_type': 'express'}
        )
        
        if not stripe_account.stripe_account_id:
            stripe_account.create_stripe_account()
        
        return redirect(stripe_account.get_onboarding_link())
    except Exception as e:
        messages.error(request, str(e))
        return redirect('parker_my_gains')

@login_required
def complete_stripe_account(request):
    try:
        stripe_account = request.user.stripe_account
        return redirect(stripe_account.get_onboarding_link())
    except Exception as e:
        messages.error(request, str(e))
        return redirect('parker_my_gains')
    

@login_required
def stripe_reauth(request, account_id):
    """Vue appelée si la session d'onboarding expire"""
    stripe_account = StripeConnectAccount.objects.get(stripe_account_id=account_id)
    return redirect('create_stripe_account')

@login_required
def stripe_return(request, account_id):
    """Vue appelée quand l'onboarding est terminé"""
    stripe_account = StripeConnectAccount.objects.get(stripe_account_id=account_id)
    
    # Vérifiez le statut du compte
    if stripe_account.check_account_status():
        messages.success(request, "Votre compte Stripe a été configuré avec succès !")
    else:
        messages.warning(request, "La configuration de votre compte Stripe n'est pas encore terminée.")
    
    # Redirigez vers la page de votre choix
    return redirect('parker_my_gains')  # ou toute autre page de votre choix


@login_required
def create_checkout_session(request, reservation_token):
    try:
        # Récupérer la réservation
        reservation = get_object_or_404(Reservation, token=reservation_token)
        reservation.name = f"{reservation.client.first_name} {reservation.client.last_name}"
        
        stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
        
        # Créer la session de paiement
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(reservation.total_price * 100),  # Stripe utilise les centimes
                    'product_data': {
                        'name': f'Réservation parking - {reservation.name}',
                        'description': f"""Réservation du {reservation.arrivee.strftime("%d/%m/%Y")} au {reservation.departure.strftime("%d/%m/%Y")}
                                         | Adresse: {reservation.place.address}""",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + f'?reservation={reservation_token}',
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
            metadata={
                'reservation_id': reservation.id,
                'client_id': request.user.id,
                'place_id': reservation.place.id
            }
        )
        return redirect(checkout_session.url)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la création du paiement: {str(e)}")
        return redirect('client_reservations_waiting_paiement')

@login_required
def payment_success(request):
    reservation_token = request.GET.get('reservation')
    if reservation_token:
        try:
            reservation = get_object_or_404(Reservation, token=reservation_token)

            # Créer l'objet payement
            pay = ReservationPayement.objects.create(
                client = reservation.client,
                parker = reservation.parker,
                reservation = reservation,
                price = reservation.price,
                commission = reservation.commission,
                total_price = reservation.total_price
            )

            pay.client_payed = True
            pay.save()
            reservation.payed = True
            reservation.save()
            messages.success(request, "Votre paiement a été effectué avec succès !")
        except Exception as e:
            messages.error(request, str(e))
    return redirect('client_reservations_waiting_paiement')

@login_required
def payment_cancel(request):
    messages.warning(request, "Le paiement a été annulé.")
    return redirect('client_reservations_waiting_paiement')
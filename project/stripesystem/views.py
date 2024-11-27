# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import StripeConnectAccount, ReservationPayement
import stripe
from django.conf import settings
from django.contrib import messages
from reservations.models import Reservation
from decimal import Decimal

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
        request.session['alert'] = str(e)
        return redirect('parker_my_gains')

@login_required
def complete_stripe_account(request):
    try:
        stripe_account = request.user.stripe_account
        return redirect(stripe_account.get_onboarding_link())
    except Exception as e:
        request.session['alert'] = str(e)
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
    
    if stripe_account.check_account_status():
        request.session['message'] = "Votre compte Stripe a été configuré avec succès !"
    else:
        request.session['alert'] = "La configuration de votre compte Stripe n'est pas encore terminée."
    
    return redirect('parker_my_gains')  

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
        return redirect('client_index')

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

            request.session['message'] = "Votre paiement a été effectué avec succès ! Vous pouvez consulter votre réservation dans la section 'En cours / à venir"
        except Exception as e:
            messages.error(request, str(e))
    return redirect('client_index')

@login_required
def payment_cancel(request):
    request.session['alert'] = "Le paiement a été annulé."
    return redirect('client_index')


@login_required
def transfer_earnings(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
        print(f"API Key: {stripe.api_key[:5]}...") # Affiche les 5 premiers caractères
        
        payments = ReservationPayement.objects.filter(
            parker=request.user,
            client_payed=True,
            parker_payed=False,
            refound_require=False
        )
        
        stripe_account = request.user.stripe_account
        print(f"Stripe Account ID: {stripe_account.stripe_account_id}")
        
        total_amount = Decimal('0.00')
        for payment in payments:
            if payment.reservation.finished and payment.client_payed and not payment.parker_payed:
                total_amount += payment.price
                print(f"Payment ID: {payment.id}, Amount: {payment.price}")

        stripe_amount = int(total_amount * 100)
        print(f"Final amount in cents: {stripe_amount}")
        
        try:
            transfer = stripe.Transfer.create(
                amount=stripe_amount,
                currency='eur',
                destination=stripe_account.stripe_account_id,
                description=f"Transfert des gains pour {len(payments)} réservations",
                metadata={'parker_id': request.user.id}
            )
            print(f"Transfer created: {transfer.id}")
            
            payments.update(parker_payed=True)
            messages.success(request, f"Transfert de {total_amount}€ effectué avec succès!")
            
        except stripe.error.StripeError as se:
            print(f"Stripe error: {se.error.message}")
            messages.error(request, f"Erreur Stripe détaillée: {se.error.message}")
            
    except Exception as e:
        import traceback
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"Erreur: {str(e)}")
        
    return redirect('parker_my_gains')
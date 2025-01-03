from django.urls import reverse
import stripe
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from reservations.models import Reservation
from django.utils import timezone


stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeConnectAccount(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='stripe_account'
    )
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(
        max_length=10,
        choices=[
            ('express', 'Express'),
            ('standard', 'Standard'),
        ],
        default='express'
    )
    onboarding_complete = models.BooleanField(default=False)

    def create_stripe_account(self):
        if not self.stripe_account_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
                
                account = stripe.Account.create(
                    type=self.account_type,
                    country='FR',
                    email=self.user.email,
                    capabilities={
                        'card_payments': {'requested': True},
                        'transfers': {'requested': True},
                    },
                    business_type='individual',
                    business_profile={
                        'url': 'http://www.parksafe.fr/',  # Votre URL
                        'mcc': '7523',  # Code pour "Parking lots and garages"
                        'product_description': 'Location de places de parking',
                    },
                )
                self.stripe_account_id = account.id
                self.save()
                return account
            except stripe.error.StripeError as e:
                print(f"Stripe Error: {str(e)}")
                raise ValidationError(str(e))

    def get_onboarding_link(self):
        if not self.stripe_account_id:
            raise ValidationError("Le compte Stripe n'a pas encore été créé")
        
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
            account_link = stripe.AccountLink.create(
                account=self.stripe_account_id,
                refresh_url="https://www.parksafe.fr/compte/mes-revenus/",
                return_url="https://www.parksafe.fr/compte/mes-revenus/",
                type="account_onboarding",
            )
            return account_link.url
        except stripe.error.StripeError as e:
            print(f"Stripe Error: {str(e)}")
            raise ValidationError(str(e))

    def check_account_status(self):
        if not self.stripe_account_id:
            return False
        
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            account = stripe.Account.retrieve(self.stripe_account_id)
            self.onboarding_complete = (
                account.details_submitted and
                account.charges_enabled and
                account.payouts_enabled
            )
            self.save()
            return self.onboarding_complete
        except stripe.error.StripeError:
            return False

    def __str__(self):
        return f"Compte Stripe de {self.user.email}"


class ReservationPayement(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='exit_payements', blank=True, null=True)
    parker = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='enter_payements', blank=True, null=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, related_name='payements', blank=True, null=True)
    
    price = models.DecimalField(verbose_name="Prix de l'hôte (en €)", max_digits=5, decimal_places=2, blank=True, null=True)
    commission = models.IntegerField(verbose_name="Commission ParkSafe", default=20)
    frais_stripe = models.DecimalField(verbose_name="Frais Stripe", max_digits=5, decimal_places=2, default=00.00)
    total_price = models.DecimalField(verbose_name="Prix de total (en €)", max_digits=5, decimal_places=2, blank=True, null=True)

    client_payed = models.BooleanField(verbose_name="Payé par le client", default=False)
    parker_payed = models.BooleanField(verbose_name='Paiement versé au loueur', default=False)
    refound_require = models.BooleanField(verbose_name='Remboursement demandé', default=False)
    refounded = models.BooleanField(verbose_name="Remboursement au client effectué", default=False)

    created_on = models.DateField(verbose_name="Date du gain", default=timezone.now)

    def __str__(self):
        client_name = f"{self.client.first_name} {self.client.last_name[0]}."
        parker_name = f"{self.parker.first_name} {self.parker.last_name[0]}."
        return f"Paiement de {client_name} vers {parker_name} - {self.total_price}€"




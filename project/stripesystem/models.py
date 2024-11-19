from django.urls import reverse
import stripe
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from accounts.models import CustomUser

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
                refresh_url="http://127.0.0.1:8000/compte/mes-revenus/",
                return_url="http://127.0.0.1:8000/compte/mes-revenus/",
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
from django.contrib import admin
from .models import StripeConnectAccount, ReservationPayement


admin.site.register(StripeConnectAccount)
admin.site.register(ReservationPayement)
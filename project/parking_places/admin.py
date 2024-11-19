from django.contrib import admin
from .models import ParkingPlace, DevenirHoteCommentCaMarcheItem, PourquoiDevenirHoteItem


class PPAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on', 'last_updated')


admin.site.register(ParkingPlace, PPAdmin)
admin.site.register(DevenirHoteCommentCaMarcheItem)
admin.site.register(PourquoiDevenirHoteItem)
from django.contrib import admin
from .models import PointOfInterest, PoiCategory, PoiCity

admin.site.register(PointOfInterest)
admin.site.register(PoiCity)
admin.site.register(PoiCategory)

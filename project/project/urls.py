from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from faq.views import move_faq_item, delete_faq_item
from accounts.views import move_devenir_hote_ccm, move_devenir_hote_pdh, delete_devenir_hote_ccm, delete_devenir_hote_pdh



urlpatterns = [
    path('admin/', admin.site.urls),
    path('compte/', include('accounts.urls')),
    path('places/', include('parking_places.urls')),
    path('', include('main.urls')),
    path('avis/', include('avis.urls')),
    path('reservation/', include('reservations.urls')),
    path('stripe/', include('stripesystem.urls')),

    path('api/faq/move/', move_faq_item, name='move_faq_item'),
    path('api/faq/delete/', delete_faq_item, name='delete_faq_item'),

    path('api/devenir-hote/move/ccm/', move_devenir_hote_ccm, name='move_devenir_hote_ccm'),
    path('api/devenir-hote/move/pdh/', move_devenir_hote_pdh, name='move_devenir_hote_pdh'),
    path('api/devenir-hote/delete/ccm/', delete_devenir_hote_ccm, name='delete_devenir_hote_ccm'),
    path('api/devenir-hote/delete/pdh/', delete_devenir_hote_pdh, name='delete_devenir_hote_pdh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
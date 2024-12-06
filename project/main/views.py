from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from faq.models import FaqItem
from interactive_map.models import PointOfInterest, PoiCategory
from django.template.response import TemplateResponse
from avis.models import AvisClientParker
from parking_places.models import CommentCaMarcheItem, PourquoiParksafeItem


def index(request):
    user = request.user
    faq_items = FaqItem.objects.all().order_by('ordre')
    last_avis = AvisClientParker.objects.filter(stars__gte=4).order_by('-created_on')[:10]
    ccm_items = CommentCaMarcheItem.objects.all().order_by('ordre')
    pq_items = PourquoiParksafeItem.objects.all().order_by('ordre')

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    context = {
        'user': user,
        'faq_items': faq_items,
        'avis_recus': last_avis,
        'today': today,
        'tomorrow': tomorrow,
        'ccm_items': ccm_items,
        'pq_items': pq_items,
    }
    return TemplateResponse(request, 'main/index.html', context)


def a_propos(request):
    faq_items = FaqItem.objects.all().order_by('ordre')
    ccm_items = CommentCaMarcheItem.objects.all().order_by('ordre')
    pq_items = PourquoiParksafeItem.objects.all().order_by('ordre')

    return TemplateResponse(request, 'main/a_propos.html', context={
        'faq_items': faq_items,
        'ccm_items': ccm_items,
        'pq_items': pq_items,
    })


def mentions_legales(request):
    return TemplateResponse(request, 'main/legales/mentions_legales.html', context={
    })

def confidentitalite(request):
    return TemplateResponse(request, 'main/legales/confidentitalite.html', context={
    })

def cgv(request):
    return TemplateResponse(request, 'main/legales/cgv.html', context={
    })




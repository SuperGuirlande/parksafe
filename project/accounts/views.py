import hashlib
import time
import json
from decimal import Decimal
from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from parking_places.models import ParkingPlace, DevenirHoteCommentCaMarcheItem, PourquoiDevenirHoteItem
from interactive_map.models import PointOfInterest
from .models import CustomUser
from .forms import MobileNumberForm, UserRegisterForm, UserLoginForm, ProfilPicForm
from faq.models import FaqItem
from faq.forms import FaqItemForm
from django.db.models import Max, F

from reservations.models import Reservation
from stripesystem.models import ReservationPayement



# General redirection
def general_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('my_account')

# S'enregistrer
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['message'] = 'Votre inscription est réussie ! Vous pouvez vous connecter'
            return redirect('login')
    else:
        form = UserRegisterForm()
    return TemplateResponse(request, 'accounts/register.html', {'form': form})

# Login
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('my_account')
            else:
                print("Authentication failed: user is None")
        else:
            print("Form is not valid")
    else:
        form = UserLoginForm()

    return TemplateResponse(request, 'accounts/login.html', {'form': form})

# Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

### CLIENT ###
# Reservations en attente d'acceptation
@login_required
def client_reservations_waiting(request):
    user = request.user
    reservations = Reservation.objects.filter(client=user, accepted=False, canceled=False, payed=False, finished=False).order_by('-id')

    context={
        'reservations': reservations,
        'user': user,
    }

    return TemplateResponse(request, 'accounts/user/client/waiting_reservations.html', context)

# Reservations en attente de paiement
@login_required
def client_reservations_waiting_paiement(request):
    user = request.user
    reservations = Reservation.objects.filter(client=user, accepted=True, payed=False, finished=False, canceled=False).order_by('-id')

    context={
        'reservations': reservations,
        'user': user,
    }

    return TemplateResponse(request, 'accounts/user/client/waiting_paiement_reservations.html', context)

# Reservation a venir / en cours
@login_required
def client_current_reservations(request):
    user = request.user
    reservations = Reservation.objects.filter(client=user, accepted=True, payed=True, canceled=False, finished=False).order_by('-id')
    print(reservations)
    context={
        'reservations': reservations,
        'user': user,
    }

    return TemplateResponse(request, 'accounts/user/client/current_reservations.html', context)  

# Reservation terminées
@login_required
def client_finished_reservations(request):
    user = request.user
    reservations = Reservation.objects.filter(client=user, accepted=True, payed=True, canceled=False, finished=True).order_by('-id')
    print(reservations)
    context={
        'reservations': reservations,
        'user': user,
    }

    return TemplateResponse(request, 'accounts/user/client/finished_reservations.html', context)   

# Annuler la reservation
@login_required
def client_cancel_reservation(request, token):
    reservation = get_object_or_404(Reservation, token=token)

    context={
        'reservation': reservation,
    }

    return TemplateResponse(request, 'accounts/user/client/cancel_reservation.html', context)

@login_required
def client_confirm_cancel(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    if request.user != reservation.client:
        return redirect('my_account')
    
    reservation.canceled = True
    reservation.save()
    request.session['message'] = "La réservation à bien été annulée"

    return redirect('client_reservations_waiting')

### LOUEUR ###
# Account mes places
@login_required
def my_account_places(request):
    user = request.user
    user_places = ParkingPlace.objects.filter(user=user)

    context = {
        'user_places': user_places,
        'api_key': settings.HERE_API_KEY,
    }

    return TemplateResponse(request, 'accounts/user/my_places.html', context)

# Reservations à traiter
@login_required
def parker_reservation_waiting(request):
    user = request.user
    reservations = Reservation.objects.filter(parker=user, accepted=False, canceled=False)

    for res in reservations:
        client = res.client
        res.name = f"{client.first_name} {client.last_name}"

    context={
        'reservations': reservations,
    }

    return TemplateResponse(request, 'accounts/user/parker/waiting_reservations.html', context)

# Refuser la demande
@login_required
def parker_cancel_reservation(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    reservation.name = f"{reservation.client.first_name} {reservation.client.last_name}"

    context={
        'reservation': reservation,
    }

    return TemplateResponse(request, 'accounts/user/parker/cancel_reservation.html', context)

@login_required
def parker_confirm_cancel(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    if request.user != reservation.parker:
        return redirect('my_account')
    
    reservation.canceled = True
    reservation.save()
    request.session['message'] = "La réservation à bien été refusée"

    return redirect('parker_reservation_waiting')

# Accepter la demande
@login_required
def parker_accept_reservation(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    user = request.user

    if reservation.parker != user:
        return redirect('parker_reservation_waiting')
    
    reservation.name = f"{reservation.client.first_name} {reservation.client.last_name}"

    context={
        'reservation': reservation,
    }

    return TemplateResponse(request, 'accounts/user/parker/accept_reservation.html', context)

@login_required
def parker_confirm_accept(request, token):
    reservation = get_object_or_404(Reservation, token=token)
    if request.user != reservation.parker:
        return redirect('parker_reservation_waiting')
    
    reservation.accepted = True
    reservation.save()
    request.session['message'] = "La réservation à bien été acceptée. Une demande de paiement à été transmise au client"

    return redirect('parker_reservation_waiting')

# Mes reservations
@login_required
def parker_my_reservations(request):
    user = request.user

    waiting_paiements = Reservation.objects.filter(parker=user, accepted=True, payed=False, canceled=False, finished=False).order_by('arrivee')
    current_reservations = Reservation.objects.filter(parker=user, accepted=True, payed=True, canceled=False, finished=False).order_by('arrivee')

    context = {
        'current_reservations': current_reservations,
        'waiting_paiements': waiting_paiements,
    }

    return TemplateResponse(request, 'accounts/user/parker/my_reservations.html', context)

# Mes revenus
@login_required
def parker_my_gains(request):
    user = request.user
    payements = ReservationPayement.objects.filter(parker=user)

    total_gains = Decimal("0.00")
    waiting_gains = Decimal("0.00")

    for pay in payements:
        if pay.reservation.finished:
            if pay.client_payed:
                total_gains += pay.price

            if not pay.parker_payed:
                waiting_gains += pay.price
    
    try:
        stripe_account = user.stripe_account
        has_stripe_account = True
        is_stripe_completed = stripe_account.check_account_status()
    except:
        has_stripe_account = False
        is_stripe_completed = False

    return TemplateResponse(request, "accounts/user/parker/my_gains.html", context={
        'has_stripe_account': has_stripe_account,
        'is_stripe_completed': is_stripe_completed,
        'total_gains': total_gains,
        'waiting_gains': waiting_gains,
    })

### GENERAL ###
# Account detail
@login_required
def my_account(request):
    user = request.user
    user_places = ParkingPlace.objects.filter(user=user)
    
    context = {
        'user': user,
        'user_places': user_places,
        'api_key': settings.HERE_API_KEY,
    }
    return TemplateResponse(request, 'accounts/my_account.html', context)


# Change password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
            request.session['message'] = 'Votre mot de passe a été modifié avec succès'
            return redirect(reverse_lazy('my_account'))
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    return TemplateResponse(request, 'accounts/password_reset/change_password.html', {'form': form})


# Change Mobile Form
@login_required
def change_mobile_number(request):
    user = request.user

    if request.method == 'POST':
        form = MobileNumberForm(request.POST)
        if form.is_valid():
            numero_normalise = form.cleaned_data['phone']
            # Vérifiez si le numéro existe déjà
            if CustomUser.objects.filter(phone=numero_normalise).exclude(id=user.id).exists():
                request.session['alert'] = 'Ce numéro de mobile a déjà été attribué à un compte.'
            else:
                try:
                    user.phone = numero_normalise
                    user.save()
                    request.session['message'] = "Votre numéro de téléphone a été mis à jour avec succès."
                    return redirect('my_account')
                except IntegrityError:
                    request.session['alert'] = "Une erreur s'est produite lors de la mise à jour du numéro de téléphone."
    else:
        initial_numb = {}

        if user.phone:
            initial_numb = {'phone': user.phone}

        form = MobileNumberForm(initial=initial_numb)

    return TemplateResponse(request, 'accounts/forms/mobile_number_form.html', {'form': form})


#  Change Profil Pic
@login_required
def change_profil_pic(request):
    user = request.user
    alert=None
    color=None

    if request.method == 'POST':
        form = ProfilPicForm(request.POST, request.FILES)
        if form.is_valid():
            user.profil_pic = form.cleaned_data['profil_pic']
            user.save()
            request.session['message'] = 'Votre image de profil a été mise à jour avec succès !'
            return redirect('my_account')
        else:
            alert="Il y a un problème avec le fichier"
    else:
        form = ProfilPicForm()

    return TemplateResponse(request, 'accounts/forms/profil_pic_form.html', {'form': form})


### ADMINISTRATEUR ###
@login_required
def admin_index(request):
    user = request.user
    if not user.is_superuser:
        return redirect('index')

    return TemplateResponse(request, "accounts/admin/admin_index.html", context={})


# FAQ ADMIN
@login_required
def faq_index(request):
    user = request.user
    if not user.is_superuser:
        return redirect('index')
    
    items = FaqItem.objects.all().order_by('ordre')

    return TemplateResponse(request, "accounts/admin/faq/faq_index.html", context={
        'items': items,
    })


@login_required
def faq_item_form(request, id=None):
    # Check SuperUser
    user = request.user
    if not user.is_superuser:
        return redirect('index')
    
    # Calcul de l'ordre du nouvel item
    items = FaqItem.objects.all()
    if not items.exists():
        initial_count = 1
    else:
        initial_count = items.count() + 1

    # Recupération de l'instance
    if id:
        instance = get_object_or_404(FaqItem, id=id)
    else:
        instance = None

    # Traitement du formulaire
    if request.method == 'POST':
        if instance:
            form = FaqItemForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('faq_index')
        else:
            form = FaqItemForm(request.POST)
            if form.is_valid():
                new_item = form.save(commit=False)
                new_item.ordre = initial_count;
                new_item.save()
                return redirect('faq_index')
    else:
        if instance:
            form = FaqItemForm(instance=instance)
        else:
            form = FaqItemForm()

    return TemplateResponse(request, "accounts/admin/faq/faq_item_form.html", context={
        'form': form,
    })

# Devenir hote admin
def devenir_hote_index(request):
    ccm_items = DevenirHoteCommentCaMarcheItem.objects.all().order_by('ordre')
    pdh_items = PourquoiDevenirHoteItem.objects.all().order_by('ordre')

    return TemplateResponse(request, 'accounts/admin/devenir_hote/devenir_hote.html', context={
        'ccm_items': ccm_items,
        'pdh_items': pdh_items,
        'hide_buttons': True,
    })

@staff_member_required
def devenir_hote_add_ccm(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        # Récupérer l'ordre maximum actuel et ajouter 1
        max_ordre = DevenirHoteCommentCaMarcheItem.objects.all().aggregate(Max('ordre'))['ordre__max'] or 0
        
        DevenirHoteCommentCaMarcheItem.objects.create(
            title=title,
            content=content,
            ordre=max_ordre + 1
        )
        return redirect('devenir_hote_index')
        
    return render(request, 'parking_places/forms/ccm_form.html')

@staff_member_required
def devenir_hote_add_pdh(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        # Récupérer l'ordre maximum actuel et ajouter 1
        max_ordre = PourquoiDevenirHoteItem.objects.all().aggregate(Max('ordre'))['ordre__max'] or 0
        
        PourquoiDevenirHoteItem.objects.create(
            title=title,
            content=content,
            ordre=max_ordre + 1
        )
        return redirect('devenir_hote_index')
        
    return render(request, 'parking_places/forms/pdh_form.html')

@staff_member_required
def devenir_hote_edit_ccm(request, id):
    item = get_object_or_404(DevenirHoteCommentCaMarcheItem, id=id)
    
    if request.method == "POST":
        item.title = request.POST.get('title')
        item.content = request.POST.get('content')
        item.save()
        return redirect('devenir_hote_index')
        
    return render(request, 'parking_places/forms/ccm_form.html', {'item': item})

@staff_member_required
def devenir_hote_edit_pdh(request, id):
    item = get_object_or_404(PourquoiDevenirHoteItem, id=id)
    
    if request.method == "POST":
        item.title = request.POST.get('title')
        item.content = request.POST.get('content')
        item.save()
        return redirect('devenir_hote_index')
        
    return render(request, 'parking_places/forms/pdh_form.html', {'item': item})

@require_POST
@staff_member_required
def move_devenir_hote_ccm(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        direction = data.get('direction')
        
        with transaction.atomic():
            current_item = get_object_or_404(DevenirHoteCommentCaMarcheItem, id=item_id)
            current_ordre = current_item.ordre
            
            if direction == 'up' and current_ordre > 1:
                swap_item = DevenirHoteCommentCaMarcheItem.objects.get(ordre=current_ordre - 1)
                swap_item.ordre = current_ordre
                current_item.ordre = current_ordre - 1
                swap_item.save()
                current_item.save()
            elif direction == 'down':
                try:
                    swap_item = DevenirHoteCommentCaMarcheItem.objects.get(ordre=current_ordre + 1)
                    swap_item.ordre = current_ordre
                    current_item.ordre = current_ordre + 1
                    swap_item.save()
                    current_item.save()
                except DevenirHoteCommentCaMarcheItem.DoesNotExist:
                    pass
                    
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@staff_member_required
def move_devenir_hote_pdh(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        direction = data.get('direction')
        
        with transaction.atomic():
            current_item = get_object_or_404(PourquoiDevenirHoteItem, id=item_id)
            current_ordre = current_item.ordre
            
            if direction == 'up' and current_ordre > 1:
                swap_item = PourquoiDevenirHoteItem.objects.get(ordre=current_ordre - 1)
                swap_item.ordre = current_ordre
                current_item.ordre = current_ordre - 1
                swap_item.save()
                current_item.save()
            elif direction == 'down':
                try:
                    swap_item = PourquoiDevenirHoteItem.objects.get(ordre=current_ordre + 1)
                    swap_item.ordre = current_ordre
                    current_item.ordre = current_ordre + 1
                    swap_item.save()
                    current_item.save()
                except PourquoiDevenirHoteItem.DoesNotExist:
                    pass
                    
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@staff_member_required
def delete_devenir_hote_ccm(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        with transaction.atomic():
            item = get_object_or_404(DevenirHoteCommentCaMarcheItem, id=item_id)
            current_ordre = item.ordre
            item.delete()
            
            # Réorganiser les ordres
            DevenirHoteCommentCaMarcheItem.objects.filter(ordre__gt=current_ordre).update(
                ordre=F('ordre') - 1
            )
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@staff_member_required
def delete_devenir_hote_pdh(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        with transaction.atomic():
            item = get_object_or_404(PourquoiDevenirHoteItem, id=item_id)
            current_ordre = item.ordre
            item.delete()
            
            # Réorganiser les ordres
            PourquoiDevenirHoteItem.objects.filter(ordre__gt=current_ordre).update(
                ordre=F('ordre') - 1
            )
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
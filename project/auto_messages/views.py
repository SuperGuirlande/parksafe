from django.shortcuts import get_object_or_404, render
from twilio.rest import Client
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from reservations.models import Reservation
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import formats

def send_sms(to_number, message_body):
    """
    Send SMS using Twilio with proper error handling
    Returns (success, error_message)
    """
    try:
        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_NUMBER,
            to=to_number
        )
        return True, None
    except Exception as e:
        return False, str(e)


# RESERVATION FAITE
def send_client_make_reserv_sms_to_parker(reservation):
    if not reservation or not reservation.place or not reservation.place.phone:
        return False, "Missing required reservation data"
    
    parker_number = str(reservation.place.phone)
    parker_confirmation_url = f"{settings.SITE_URL}/compte/hote/mes-reservations/#a-confirmer"
    
    # TO PARKER
    message = f"""Vous avez reçu une nouvelle demande de réservation !
    
Consultez les détails et répondez rapidement ici : {parker_confirmation_url}  🚗"""

    success, error = send_sms(parker_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au parker: {error}"
    print(f"Message envoyé avec succès à {parker_number}")

    return True, None

def send_client_make_reserv_sms_to_client(reservation):
    if not reservation or not reservation.place or not reservation.place.phone:
        return False, "Missing required reservation data"
    
    client_number = str(reservation.phone)
    client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#en-attente"
    
    # TO CLIENT
    message = f"""Votre demande de réservation chez {reservation.parker.first_name} {reservation.parker.last_name} a été envoyée. 
    
L'hôte dispose de 24h pour répondre. Consultez les détails ici : {client_confirmation_url}   🚗"""

    success, error = send_sms(client_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au client: {error}"
    print(f"Message envoyé avec succès à {client_number}")

    return True, None

def send_client_make_reserv_email(reservation):
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"
        parker_confirmation_url = f"{settings.SITE_URL}/compte/hote/mes-reservations/#a-confirmer"
        client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#en-attente"

        # TO PARKER
        to_email = reservation.parker.email
        subject = "📭 Nouvelle demande de réservation reçue !"
        content = f"""Bonjour {reservation.parker.first_name},
Vous avez reçu une nouvelle demande de réservation pour votre espace de stationnement !

Connectez-vous à votre tableau de bord pour consulter les détails et répondre à la demande : {parker_confirmation_url}

Merci de réagir rapidement pour maximiser vos chances de confirmation.

L'équipe ParkSafe 🚗✨
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()
        arrivee_formatted = formats.date_format(reservation.arrivee, format="l j F Y à H:h")  
        departure_formatted = formats.date_format(reservation.departure, format="l j F Y à H:h")
        # TO CLIENT
        to_email = reservation.client.email
        subject = "📭 Nouvelle demande de réservation envoyée !"
        content = f"""Bonjour {reservation.client.first_name},

Votre demande de réservation a été envoyée avec succès ! Voici les détails :
    • Hôte : {reservation.parker.first_name} {reservation.parker.last_name}
    • Adresse du stationnement : {reservation.place.address}
    • Dates de réservation : {arrivee_formatted} - {departure_formatted}
    • Prix total : {reservation.total_price}€

👉 Et maintenant ?
L'hôte dispose de 24 heures pour accepter ou refuser votre demande. Vous recevrez une notification
dès qu'il aura répondu.

En attendant, vous pouvez effectuez une autre demande parmi nos hôtes pour maximiser vos
chances de retour positif.

Merci de faire confiance à ParkSafe pour votre stationnement ! 🚗✈️

À bientôt,
L'équipe ParkSafe
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
        print(e)
        return False, str(e)



# RESERVATION ACCEPTEE
def send_parker_accept_reserv_sms_to_client(reservation):
    if not reservation or not reservation.place or not reservation.place.phone:
        return False, "Missing required reservation data"
    
    client_number = str(reservation.phone)
    client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#attente-de-paiement"
    
    # TO CLIENT
    message = f"""Votre demande de réservation a été acceptée ! 
    
Procédez au paiement sous 48h pour la finaliser {client_confirmation_url} 🚗"""

    success, error = send_sms(client_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au client: {error}"
    print(f"Message envoyé avec succès à {client_number}")

    return True, None


def send_parker_accept_reserv_email(reservation):
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"
        client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#attente-de-paiement"
        arrivee_formatted = formats.date_format(reservation.arrivee, format="l j F Y à H:h")  
        departure_formatted = formats.date_format(reservation.departure, format="l j F Y à H:h")
        # TO CLIENT
        to_email = reservation.client.email
        subject = "✅ Votre demande de réservation a été acceptée : Passez au paiement ! "
        content = f"""Bonjour {reservation.client.first_name},

Bonne nouvelle, votre demande de réservation a été acceptée par {reservation.parker.first_name} {reservation.parker.last_name}

Voici les détails :
    • Hôte : {reservation.parker.first_name} {reservation.parker.last_name}
    • Dates de réservation : {arrivee_formatted} - {departure_formatted}
    • Prix total : {reservation.total_price}€
    • Nombre de passagers : {reservation.passengers}

👉 Prochaine étape : Procédez au paiement sous 48 heures pour finaliser la réservation.

Sans paiement, votre réservation sera annulée automatiquement.

Lien : {client_confirmation_url}

Merci d'avoir choisi ParkSafe, et bon voyage ! 🚗✈️

L'équipe ParkSafe
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
        return False, str(e)



# RESERVATION PAYEE
def send_client_payed_reserv_sms_to_parker(reservation):
    if not reservation or not reservation.place or not reservation.place.phone:
        return False, "Missing required reservation data"
    
    parker_number = str(reservation.place.phone)
    client_number = str(reservation.phone)
    parker_confirmation_url = f"{settings.SITE_URL}/compte/hote/mes-reservations/#mes-reservations"
    
    # TO PARKER
    message = f"""Bonne nouvelle ! 
    
{reservation.client.first_name} {reservation.client.last_name} a finalisé le paiement pour sa réservation. 

Vous pouvez le joindre directement au {client_number}. 

Consultez les détails de la réservation ici : {parker_confirmation_url} 

🚗"""

    success, error = send_sms(parker_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au parker: {error}"
    print(f"Message envoyé avec succès à {parker_number}")

    return True, None

def send_client_payed_reserv_sms_to_client(reservation):
    if not reservation or not reservation.place or not reservation.place.phone:
        return False, "Missing required reservation data"
    
    client_number = str(reservation.phone)
    parker_number = str(reservation.place.phone)
    client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#en-cours"
    
    # TO CLIENT
    message = f"""Votre paiement a été reçu ! Votre réservation est confirmée et finalisée.
    
Coordonnées de l'hôte :
    • Nom de l'hôte : {reservation.parker.first_name} {reservation.parker.last_name}
    • Adresse du stationnement : {reservation.place.address}
    • Téléphone de l'hôte : {parker_number}

Consultez les détails ici : {client_confirmation_url}

Bon voyage ! 🚗✈️
"""

    success, error = send_sms(client_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au client: {error}"
    print(f"Message envoyé avec succès à {client_number}")

    return True, None


def send_client_payed_reserv_email(reservation):
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"
        parker_confirmation_url = f"{settings.SITE_URL}/compte/hote/mes-reservations/#mes-reservations"
        client_confirmation_url = f"{settings.SITE_URL}/compte/mes-reservations/#en-cours"
        client_number = str(reservation.phone)
        parker_number = str(reservation.place.phone)
        arrivee_formatted = formats.date_format(reservation.arrivee, format="l j F Y à H:h")  
        departure_formatted = formats.date_format(reservation.departure, format="l j F Y à H:h")
        # TO PARKER
        to_email = reservation.parker.email
        subject = f"💰 {reservation.client.first_name} {reservation.client.last_name} à finalisé sa réservation !"
        content = f"""Bonjour {reservation.parker.first_name},
Bonne nouvelle ! {reservation.client.first_name} {reservation.client.last_name} a finalisé le paiement pour sa réservation.

Détails de la réservation :
    • Voyageur : {reservation.client.first_name} {reservation.client.last_name}
    • Dates de réservation : {arrivee_formatted} - {departure_formatted}
    • Adresse de stationnement : {reservation.place.address}

Vous pouvez maintenant contacter le voyageur directement par téléphone au {client_number}.

👉 Consultez les détails complets de la réservation ici : {parker_confirmation_url}

L'équipe ParkSafe 🚗✨
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()
        arrivee_formatted = formats.date_format(reservation.arrivee, format="l j F Y à H:h")  
        departure_formatted = formats.date_format(reservation.departure, format="l j F Y à H:h")
        # TO CLIENT
        to_email = reservation.client.email
        subject = "🎉 Réservation confirmée : Votre stationnement est prêt !"
        content = f"""Bonjour {reservation.client.first_name},

Félicitations, votre paiement a été reçu et votre réservation est maintenant confirmée ! 
Voici les détails :
    • Hôte : {reservation.parker.first_name} {reservation.parker.last_name}
    • Adresse du stationnement : {reservation.place.address}
    • Téléphone de l'hôte : {parker_number}
    • Dates de réservation : {arrivee_formatted} - {departure_formatted}
    • Prix total : {reservation.total_price}€

👉 Prochaine étape :
Votre hôte vous communiquera prochainement les instructions pour accéder au stationnement. Si
vous avez des questions, n'hésitez pas à le contacter directement.

Consultez les détails de votre réservation ici : {client_confirmation_url}

Merci d'avoir choisi ParkSafe, et bon voyage !  🚗✈️

À bientôt,
L'équipe ParkSafe
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
        return False, str(e)


# COMPTE CREE
def send_account_created_mail(user):
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"
        connect_url = f"{settings.SITE_URL}/compte/se-connecter/"

        to_email = user.email
        subject = f"🎉 Bienvenue sur ParkSafe ! Votre compte est prêt"
        content = f"""Bonjour {user.first_name},

Félicitations, votre compte ParkSafe a été créé avec succès ! Vous pouvez désormais :
    • Rechercher et réserver des stationnements privés près des aéroports.
    • Proposer votre espace de stationnement à la location.

👉 Connectez-vous dès maintenant : {connect_url}

Nous sommes ravis de vous compter parmi nous et restons à votre disposition pour toute question.

Merci de faire partie de la communauté ParkSafe, et à bientôt !

L'équipe ParkSafe 🚗✨

"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
            return False, str(e)



# ANNONCE CREE
def send_place_created_sms(place):
    parker_number = str(place.phone)
    
    # TO PARKER
    message = f"""Votre annonce ParkSafe a été créée avec succès ! 🎉
    
Elle sera vérifiée par notre équipe sous 24h avant d'être mise en ligne. 

Vous serez informé dès qu'elle sera active. 🚗✨
"""

    success, error = send_sms(parker_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au parker: {error}"
    print(f"Message envoyé avec succès à {parker_number}")

    return True, None

def send_place_created_mail(place):
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"

        to_email = place.user.email
        subject = f"📋 Votre annonce est en cours de vérification"
        content = f"""Bonjour {place.user.first_name},

Merci d'avoir créé une annonce sur ParkSafe ! 🎉

Votre annonce est actuellement en cours de vérification par notre équipe. Ce processus peut prendre
jusqu'à 24 heures. Une fois validée, votre espace de stationnement sera mis en ligne et visible par
les voyageurs.

👉 Vous serez informé par e-mail dès que votre annonce sera publiée.

Merci de votre confiance,
L'équipe ParkSafe 🚗✨
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
            return False, str(e)



# ANNONCE VERIFIE
def send_place_checked_sms(place):
    parker_number = str(place.phone)
    confirmation_url = f"{settings.SITE_URL}/places/detail-de-la-place/{place.token}/"
    
    # TO PARKER
    message = f"""Votre annonce ParkSafe a été validée et est désormais en ligne ! 🎉
    
Les voyageurs peuvent maintenant la réserver.

Consultez-la ici : {confirmation_url}

🚗✨
"""

    success, error = send_sms(parker_number, message)
    if not success:
        return False, f"Échec d'envoi SMS au parker: {error}"
    print(f"Message envoyé avec succès à {parker_number}")

    return True, None


def send_place_checked_mail(place):
    confirmation_url = f"{settings.SITE_URL}/places/detail-de-la-place/{place.token}/"
    try:
        from_email = "ParkSafe <noreply@park-safe.fr>"

        to_email = place.user.email
        subject = f"🎉 Votre annonce est maintenant en ligne !"
        content = f"""Bonjour {place.user.first_name},

Bonne nouvelle ! Votre annonce a été vérifiée et est désormais en ligne. Les voyageurs peuvent
maintenant la consulter et effectuer des réservations.

👉 Consultez votre annonce ici : {confirmation_url}


Suivi des notifications

Pour vous accompagner, vous recevrez des SMS et e-mails tout au long du processus de réservation :
    • Lorsque vous recevez une demande de réservation.
    • Lorsque le voyageur finalise la réservation en procédant au paiement. 

    
Important

Il est crucial de traiter les demandes de réservation le plus rapidement possible afin d'éviter que le
voyageur ne finalise sa réservation ailleurs. Une réponse rapide améliore votre visibilité et votre
taux de réservation.

Merci de faire partie de la communauté ParkSafe ! 🚗✨

L'équipe ParkSafe
"""

        email = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=[to_email]
        )
        email.send()

    except Exception as e:
            return False, str(e)
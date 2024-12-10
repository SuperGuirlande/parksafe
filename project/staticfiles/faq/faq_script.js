const questions = document.querySelectorAll(".question-card");

questions.forEach(question => {
    question.addEventListener('click', (e) => {
        // Ignorer le clic si c'est sur un bouton de réorganisation
        if (e.target.classList.contains('btn-move')) {
            return;
        }
        
        const targetId = question.dataset.target;
        const reponse = document.getElementById(targetId);
        const pointer = question.querySelector(".pointer");

        pointer.classList.toggle('active');
        reponse.classList.toggle('visible');
        
        if (reponse.style.maxHeight) {
            reponse.style.maxHeight = null;
            reponse.style.marginTop = "0";
        } else {
            reponse.style.maxHeight = reponse.scrollHeight + "px";
            reponse.style.marginTop = "2.5rem";
        }
    });
});

// Nouvelle fonction pour la réorganisation
async function moveItem(itemId, direction, event) {
    // Empêcher la propagation du clic pour ne pas déclencher l'animation
    event.stopPropagation();
    
    try {
        const response = await fetch('/api/faq/move/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                item_id: itemId,
                direction: direction
            })
        });

        if (!response.ok) {
            throw new Error('Erreur réseau');
        }

        const data = await response.json();
        if (data.success) {
            window.location.reload();
        } else {
            alert('Erreur lors du déplacement de l\'item');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue');
    }
}

// 1. Déclaration de la fonction deleteItem
async function deleteItem(itemId, event) {
    // 2. Empêcher la propagation du clic (comme pour moveItem)
    event.stopPropagation();
    
    // 3. Demander confirmation à l'utilisateur
    if (!confirm("Êtes-vous sûr de vouloir supprimer cette question ?")) {
        return; // Si l'utilisateur clique sur "Annuler", on arrête là
    }
    
    try {
        // 4. Envoi de la requête au serveur
        const response = await fetch('/api/faq/delete/', {
            method: 'POST',  // Méthode HTTP POST
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // On réutilise la fonction getCookie qu'on a déjà
            },
            body: JSON.stringify({
                item_id: itemId  // On envoie l'ID de l'item à supprimer
            })
        });

        // 5. Vérification de la réponse
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }

        // 6. Traitement de la réponse
        const data = await response.json();
        if (data.success) {
            // 7. Si succès, on recharge la page
            window.location.reload();
        } else {
            // 8. Si erreur côté serveur, on affiche le message d'erreur
            alert(data.error || 'Erreur lors de la suppression de l\'item');
        }
    } catch (error) {
        // 9. Si erreur technique, on l'affiche
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de la suppression');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const btn = document.getElementById('more_btn')
const dynamics = document.getElementsByClassName('dynamic')

btn.addEventListener('click', function() {
    Array.from(dynamics).forEach((d) => {
        // Perform actions on each element
        d.classList.toggle('hidden')
    });
    console.log(btn.innerText)
    if (btn.innerText == "VOIR PLUS") {
        btn.innerText = "VOIR MOINS"
    } else {
        btn.innerText = "VOIR PLUS"
    }
});
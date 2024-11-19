from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F
from .models import FaqItem
import json

@require_POST
def move_faq_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        direction = data.get('direction')
        
        with transaction.atomic():
            current_item = FaqItem.objects.get(id=item_id)
            current_ordre = current_item.ordre
            
            if direction == 'up' and current_ordre > 1:
                # Trouver l'item au-dessus et échanger les positions
                swap_item = FaqItem.objects.get(ordre=current_ordre - 1)
                swap_item.ordre = current_ordre
                current_item.ordre = current_ordre - 1
                swap_item.save()
                current_item.save()
                
            elif direction == 'down':
                # Vérifier s'il existe un item en-dessous
                try:
                    swap_item = FaqItem.objects.get(ordre=current_ordre + 1)
                    swap_item.ordre = current_ordre
                    current_item.ordre = current_ordre + 1
                    swap_item.save()
                    current_item.save()
                except FaqItem.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Cannot move down'})
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@require_POST
def delete_faq_item(request):
    try:
        # 1. Récupérer l'ID de l'item à supprimer
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        with transaction.atomic():  # Important pour la cohérence des données
            # 2. Récupérer l'item à supprimer
            item_to_delete = FaqItem.objects.get(id=item_id)
            current_ordre = item_to_delete.ordre
            
            # 3. Supprimer l'item
            item_to_delete.delete()
            
            # 4. Réorganiser les ordres des items suivants
            FaqItem.objects.filter(ordre__gt=current_ordre).update(
                ordre=F('ordre') - 1
            )
            
        return JsonResponse({'success': True})
        
    except FaqItem.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Item non trouvé'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })
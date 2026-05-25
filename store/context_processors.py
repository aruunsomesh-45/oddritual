from .models import CartItem

def cart_count(request):
    if not request.session.session_key:
        return {'cart_count': 0}
    
    session_key = request.session.session_key
    total_qty = sum(item.quantity for item in CartItem.objects.filter(session_key=session_key))
    return {'cart_count': total_qty}

from django.shortcuts import render
import razorpay,json
from django.conf import settings
from django.http import JsonResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from payments.models import Razorpay_order,invoice
from store.models import shop_page, CartItem
from django.core.mail import send_mail
# Create your views here.
client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

def create_orders(request):
    if request.method == "POST":
        try:
            # Check if cart items exist in the active session
            session_key = request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key) if session_key else []
            
            if cart_items and cart_items.exists():
                price_in_rupees = sum(item.subtotal() for item in cart_items)
            else:
                # Fallback to single product_id from body
                data = json.loads(request.body)
                product_id = data.get('product_id')
                product = shop_page.objects.get(product_id=product_id)
                price_in_rupees = product.price
                
            price_in_paise = int(price_in_rupees * 100)
            
            # create a razorpay order and record the response 
            razorpay_order_data = {
                'amount': price_in_paise,
                'currency': 'INR',
                'payment_capture': '1',
            }
            razorpay_response = client.order.create(data=razorpay_order_data)
            
            # create the pending order in the database
            db_order = Razorpay_order.objects.create(
                order_id=razorpay_response['id'],
                amount=price_in_rupees,
                paid=False,
            )
            
            # return the order information to the UI layer
            return JsonResponse({
                'order_id': razorpay_response['id'],
                'amount': price_in_paise,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
            })
        except shop_page.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest('invalid Request')

@csrf_exempt
def verify_payments(request):
    # getting the details from ui and verify the order_id, payment_id ,signature
    if request.method=='POST':
        try:
            payment_id=request.POST.get('payment_id','')
            order_id=request.POST.get('razorpay_order_id','')
            signature=request.POST.get('razorpay_signature','')
            
            # get user details
            product_id=request.POST.get('product_id','')
            customer_name=request.POST.get('customer_name','')
            phone=request.POST.get('phone','')
            user_email=request.POST.get('email','')
            address=request.POST.get('address','')
            
            # verification of the signature and save it the db
            verify_dict={
                'razorpay_order_id':order_id,
                'razorpay_payment_id':payment_id,
                'razorpay_signature':signature,
            }
            try:
                client.utility.verify_payment_signature(verify_dict)
            except:
                return JsonResponse({'status':'failed','message':'invalid signature /mismatch signature !'},status=400)
                
            # updating the paymentdetails and status to database..
            try:
                order=Razorpay_order.objects.get(order_id=order_id)
                order.paid=True
                order.payment_id=payment_id
                order.signature=signature
                order.save()
            except Razorpay_order.DoesNotExist:
                return JsonResponse({'status':'failed','message':'order not found!'},status=404)
                
            # generate invoice id
            new_invoice=invoice.objects.create(
                razorpay_order=order,
                invioce_id=f"INV-{order_id}",
                customername=customer_name,
                email=user_email,
                phonenumber=phone,
                shippingaddress=address,
                payment_status='paid',
                total_amount=order.amount
            )
            
            # Add products to ManyToMany relation & clear CartItem objects
            session_key = request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key) if session_key else []
            
            if cart_items and cart_items.exists():
                for item in cart_items:
                    try:
                        p = shop_page.objects.get(product_id=item.product_id)
                        new_invoice.products.add(p)
                    except shop_page.DoesNotExist:
                        pass
                # Clear the cart items
                cart_items.delete()
            else:
                # Fallback to single product_id if cart is empty
                if product_id:
                    try:
                        p = shop_page.objects.get(product_id=product_id)
                        new_invoice.products.add(p)
                    except shop_page.DoesNotExist:
                        pass
                        
            return JsonResponse({'status':'success','message':'payment verified successfully and invoice has been generated' })
        except Exception as e:
            return JsonResponse({'error':str(e)},status=400)
    return HttpResponseBadRequest('invalivd request')
def process_checkout(request):
    user_gmail = request.POST.get('email')
    user_name = request.POST.get('name')
    
    # Dummy product data (replace with actual cart query)
    products = [{'name': 'Sample Product 1', 'qty': 1, 'price': 500}]
    
    # 1. Format products into a string compactly
    details = "\n".join([f"- {p['name']} (x{p['qty']}): ₹{p['price']}" for p in products])
    total = sum(p['price'] * p['qty'] for p in products)

    # 2. Simplified f-string message
    message = f"Hi {user_name},\n\nOrder Confirmed!\n\n{details}\nTotal: ₹{total}\n\nThanks,\nOdd Ritual"

    # 3. Send mail
    send_mail("Order Invoice", message, settings.EMAIL_HOST_USER, [user_gmail])
    
    return JsonResponse({'status': 'success'})
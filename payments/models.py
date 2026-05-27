from django.db import models

# Create your models here.
class Razorpay_order(models.Model):
    order_id=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    #paid is for checking payment is done or not
    paid=models.BooleanField(default=False)
    payment_id=models.CharField(max_length=100,null=True,blank=True)
    signature=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"{self.order_id} | {self.paid}"   
class invoice(models.Model):
    razorpay_order=models.OneToOneField(Razorpay_order, on_delete=models.CASCADE, null=True, blank=True)
    invoice_id=models.CharField(max_length=100, unique=True, default="PENDING")
    # multiple product details from product table
    products=models.ManyToManyField('store.shop_page', blank=True)
    customername=models.CharField(max_length=100, default="Unknown")
    phonenumber=models.CharField(max_length=15, default="0000000000")
    email=models.EmailField(null=True, blank=True)
    shippingaddress=models.TextField(max_length=500, default="Not Provided")
    total_amount=models.DecimalField(max_digits=10,decimal_places=2)
    payment_status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.invoice_id}-{self.customername}"
    
    


   
     
    
 
     

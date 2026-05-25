from django.db import models

# Create your models here.
class home_product(models.Model):
    name = models.CharField(max_length=30)
    main_image = models.ImageField(upload_to='images')
    hover_image = models.ImageField(upload_to='images')
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    product_id = models.CharField(max_length=20) 

    def __str__(self):
        return self.name

class shop_page(models.Model):
    product_name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    product_id = models.CharField(max_length=20)
    product_decription = models.TextField(max_length=1000)  
    washcare = models.TextField(max_length=1000)
    garment_details = models.TextField(max_length=1000)
    product_image1 = models.ImageField(upload_to='images')  
    product_image2 = models.ImageField(upload_to='images')    
    product_image3 = models.ImageField(upload_to='images')    
    product_image4 = models.ImageField(upload_to='images')
    product_image5 = models.ImageField(upload_to='images')    
    product_image6 = models.ImageField(upload_to='images')    
    product_image7 = models.ImageField(upload_to='images')    
    product_image8 = models.ImageField(upload_to='images')    
    product_image9 = models.ImageField(upload_to='images')    
    
    def __str__(self):
        return self.product_name
    
class community(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images')
    description = models.TextField(max_length=1000) 
    link = models.URLField() 

    def __str__(self):
        return self.name
    
class aboutpage_images(models.Model):
    image1 = models.ImageField(upload_to='images')
    image2 = models.ImageField(upload_to='images')
    image3 = models.ImageField(upload_to='images')    
    image4 = models.ImageField(upload_to='images')
    image5 = models.ImageField(upload_to='images')    

    def __str__(self):
        return f"About Page Images Set {self.id}"

class contactpage(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=10)    
    address = models.CharField(max_length=20)
    instagram = models.URLField()    
    twitter = models.URLField() 
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class contactform(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    message = models.TextField(max_length=1000, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return f"message from {self.name}, {self.email}, submitted at {self.submitted_at}"

class CartItem(models.Model):
    session_key = models.CharField(max_length=40)
    product_id = models.CharField(max_length=20)
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    product_image = models.CharField(max_length=500, blank=True, default='')
    size = models.CharField(max_length=10, blank=True, default='')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} ({self.size}) x{self.quantity}"

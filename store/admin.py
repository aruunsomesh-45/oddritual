from django.contrib import admin
from .models import home_product, shop_page, community, aboutpage_images, contactpage, contactform, CartItem

# Register your models here.
admin.site.register(home_product)
admin.site.register(shop_page)
admin.site.register(community)
admin.site.register(aboutpage_images)
admin.site.register(contactpage)
admin.site.register(contactform)
admin.site.register(CartItem)

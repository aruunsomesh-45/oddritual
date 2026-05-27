from django.contrib import admin
from .models import Razorpay_order, invoice

# Register your models here.

@admin.register(Razorpay_order)
class RazorpayOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount', 'paid', 'created_at')
    list_filter = ('paid',)
    search_fields = ('order_id', 'payment_id')
    readonly_fields = ('created_at',)

@admin.register(invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'customername', 'email', 'total_amount', 'payment_status', 'created_at')
    list_filter = ('payment_status',)
    search_fields = ('invoice_id', 'customername', 'email')
    readonly_fields = ('created_at',)

from django.contrib import admin

from .models import User, Order, OrderItem


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Модель UserAdmin."""

    list_display = ('id', 'username')
    search_fields = ('username',)
    list_filter = ('username',)
    list_display_links = ('username',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Модель OrderAdmin."""

    list_display = ('id', 'order_number', 'created_at',
                    'total_amount', 'status')
    search_fields = ('order_number', 'created_at',
                     'total_amount', 'status')
    list_filter = ('order_number', 'created_at',
                   'total_amount', 'status')
    list_display_links = ('order_number',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Модель OrderItemAdmin."""

    list_display = ('id', 'sku', 'name',
                    'quantity', 'price')
    search_fields = ('sku', 'name',
                     'quantity', 'price')
    list_filter = ('sku', 'name',
                   'quantity', 'price')
    list_display_links = ('name',)

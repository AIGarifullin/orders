from django.contrib import admin

from .models import DailyOrderStats, Order, OrderItem, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Модель UserAdmin."""

    list_display = ('id', 'username')
    search_fields = ('username',)
    list_filter = ('username',)
    list_display_links = ('username',)


class OrderItemInline(admin.TabularInline):
    """Модель OrderItemInline (для отображения товаров заказа в админке)."""

    model = OrderItem
    extra = 1
    fields = ('sku', 'name', 'quantity', 'price', 'total_price')
    readonly_fields = ('total_price',)

    def total_price(self, obj):
        """Метод для расчета общей стоимости позиции."""
        if obj.quantity is None or obj.price is None:
            return '0.00 ₽'
        return f'{obj.quantity * obj.price:.2f} ₽'

    total_price.short_description = 'Общая стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Модель OrderAdmin."""

    list_display = ('user', 'order_number', 'created_at',
                    'total_amount', 'status')
    search_fields = ('user__username', 'order_number', 'created_at',
                     'total_amount')
    list_filter = ('user', 'order_number', 'created_at',
                   'total_amount', 'status')
    list_display_links = ('order_number',)
    readonly_fields = ('created_at',)
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Модель OrderItemAdmin."""

    list_display = ('order', 'sku', 'name',
                    'quantity', 'price', 'total_price')
    search_fields = ('sku', 'name', 'order__order_number',
                     'quantity', 'price')
    list_filter = ('order__user', 'order')
    list_display_links = ('name',)

    def total_price(self, obj):
        """Метод расчета общей стоимости позиции."""
        if obj.quantity is None or obj.price is None:
            return '0.00 ₽'
        return f"{obj.quantity * obj.price:.2f} ₽"

    total_price.short_description = 'Общая стоимость'


@admin.register(DailyOrderStats)
class DailyOrderStatsAdmin(admin.ModelAdmin):
    """Модель DailyOrderStatsAdmin."""

    list_display = ('date', 'total_users', 'total_orders',
                    'total_revenue', 'avg_order_value')
    list_filter = ('date',)
    readonly_fields = ('created_at',)
    ordering = ('-date',)

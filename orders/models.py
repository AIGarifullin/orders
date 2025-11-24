from decimal import Decimal

from django.db import models

from core.constants import OrderConstants


class User(models.Model):
    """Модель User (Пользователь)."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=OrderConstants.MAX_USERNAME_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Order(models.Model):
    """Модель Order (Заказ)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='orders'
    )
    order_number = models.CharField(
        verbose_name='Номер заказа',
        max_length=OrderConstants.MAX_ORDER_NUMBER,
        unique=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания'
    )
    total_amount = models.DecimalField(
        verbose_name='Общая сумма заказа',
        max_digits=OrderConstants.MAX_TOTAL_AMOUNT,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES
    )
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=OrderConstants.MAX_STATUS_LENGTH
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('created_at',)

    def __str__(self):
        return f'Пользователь {self.user} сделал заказ № {self.order_number}'


class OrderItem(models.Model):
    """Модель OrderItem (Товар)."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name="items")
    sku = models.CharField(
        verbose_name='Артикул товара',
        max_length=OrderConstants.MAX_SKU_LENGTH)
    name = models.CharField(
        verbose_name='Название товара',
        max_length=OrderConstants.MAX_ORDER_ITEM_NAME)
    quantity = models.PositiveIntegerField(
        verbose_name='Количество товара'
    )
    price = models.DecimalField(
        verbose_name='Стоимость товара',
        max_digits=OrderConstants.MAX_PRICE_DIGITS,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)

    def __str__(self):
        return self.name


class DailyOrderStats(models.Model):
    """Модель DailyOrderStats (хранения ежедневной статистики заказов)."""

    date = models.DateField(
        verbose_name='Дата статистики',
        unique=True
    )
    total_users = models.PositiveIntegerField(
        verbose_name='Всего пользователей',
        default=0
    )
    total_orders = models.PositiveIntegerField(
        verbose_name='Всего заказов',
        default=0
    )
    total_revenue = models.DecimalField(
        verbose_name='Общая выручка',
        max_digits=OrderConstants.MAX_TOTAL_AMOUNT,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES,
        default=Decimal('0')
    )
    avg_order_value = models.DecimalField(
        verbose_name='Средний чек',
        max_digits=OrderConstants.MAX_PRICE_DIGITS,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES,
        default=Decimal('0')
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Ежедневная статистика заказов'
        verbose_name_plural = 'Ежедневная статистика заказов'
        ordering = ('-date',)

    def __str__(self):
        return f'Статистика за {self.date}'

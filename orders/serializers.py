import logging

from django.db import transaction
from rest_framework import serializers

from core.constants import OrderConstants

from .models import User, Order, OrderItem


logger = logging.getLogger('orders')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('username',)


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem."""

    class Meta:
        model = OrderItem
        fields = ('sku', 'name', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order."""

    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('order_number', 'created_at', 'total_amount',
                  'status', 'items')
        extra_kwargs = {
            'order_number': {'validators': []}
        }


class OrderUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки заказов."""

    user = serializers.CharField(max_length=OrderConstants.MAX_USERNAME_LENGTH)
    orders = OrderSerializer(many=True)

    def validate_user(self, value):
        """Метод валидации пользователя."""
        logger.debug(f'Валидация пользователя: {value}.')
        if not value.strip():
            logger.warning('Получено пустое имя пользователя.')
            raise serializers.ValidationError(
                'Имя пользователя не может быть пустым.'
            )
        logger.info(f'Пользователь прошел валидацию: {value}.')
        return value.strip()

    def validate_orders(self, value):
        """Метод валидации списка заказов."""
        logger.debug(f'Валидация {len(value)} заказа(ов).')

        if not value:
            logger.error('Получен пустой список заказов.')
            raise serializers.ValidationError(
                'Список заказов не может быть пустым.'
            )

        order_numbers = [order['order_number'] for order in value]
        if len(order_numbers) != len(set(order_numbers)):
            logger.warning(
                f'Обнаружены дубликаты order_number: {order_numbers}.'
            )
            raise serializers.ValidationError(
                'Номер(а) заказа(ов) должны быть уникальными.'
            )

        logger.info(
            f'Успешная валидация {len(value)} заказа(ов) '
            f'с номером(ами): {order_numbers}.'
        )
        return value

    def create(self, validated_data):
        """Метод создания или обновления данных заказа."""
        user_data = validated_data['user']
        orders_data = validated_data['orders']

        logger.info(
            f'Начало обработки заказа(ов) для пользователя: {user_data}.'
        )
        logger.debug(f'Количество заказов: {len(orders_data)}.')

        with transaction.atomic():
            user, created = User.objects.get_or_create(username=user_data)
            if created:
                logger.info(f'Создан новый пользователь: {user.username}.')
            else:
                logger.debug(
                    f'Найден существующий пользователь: {user.username}.'
                )

            orders_to_create = []
            orders_to_update = []
            order_items_to_create = []

            order_numbers = [
                order_data['order_number'] for order_data in orders_data
            ]
            existing_orders = Order.objects.filter(
                order_number__in=order_numbers
            )
            existing_orders_dict = {
                order.order_number: order for order in existing_orders
            }

            logger.debug(
                f'Найдено существующих заказов: {len(existing_orders_dict)}.'
            )

            for order_data in orders_data:
                items_data = order_data.pop('items')
                order_number = order_data['order_number']

                if order_number in existing_orders_dict:
                    order = existing_orders_dict[order_number]
                    for attr, value in order_data.items():
                        setattr(order, attr, value)
                    order.user = user
                    orders_to_update.append(order)
                    logger.debug(
                        f'Заказ {order_number} подготовлен к обновлению.'
                    )
                else:
                    order = Order(user=user, **order_data)
                    orders_to_create.append(order)
                    logger.debug(
                        f'Заказ {order_number} подготовлен к созданию.'
                    )

                deleted_count, _ = OrderItem.objects.filter(
                    order=order
                ).delete()
                if deleted_count > 0:
                    logger.debug(
                        f'Удалено {deleted_count} старых товаров '
                        f'из заказа {order_number}.'
                    )

                order_items = [
                    OrderItem(order=order,
                              **item_data
                              ) for item_data in items_data
                ]
                order_items_to_create.extend(order_items)
                logger.debug(
                    f'Подготовлено {len(order_items)} товаров '
                    f'для заказа {order_number}.')

            if orders_to_create:
                Order.objects.bulk_create(orders_to_create)
                logger.info(
                    f'Создано {len(orders_to_create)} новых заказов).'
                )

            if orders_to_update:
                Order.objects.bulk_update(
                    orders_to_update,
                    ['user', 'created_at', 'total_amount', 'status'])
                logger.info(
                    f'Обновлено {len(orders_to_update)} существующих заказов.'
                )

            if order_items_to_create:
                OrderItem.objects.bulk_create(order_items_to_create)
                logger.info(
                    f'Создано {len(order_items_to_create)} товаров.'
                )

            result = {
                'user': user,
                'created_orders': len(orders_to_create),
                'updated_orders': len(orders_to_update),
                'created_items': len(order_items_to_create)
            }

            logger.info(
                f'Успешно обработаны заказы для {user.username}. '
                f'Создано: {len(orders_to_create)} заказов, '
                f'Обновлено: {len(orders_to_update)} заказов, '
                f'Создано: {len(order_items_to_create)} товаров.'
            )

            return result


class UserStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики пользователя."""

    user = serializers.CharField(
        max_length=OrderConstants.MAX_USERNAME_LENGTH
    )
    orders_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(
        max_digits=OrderConstants.MAX_TOTAL_AMOUNT,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES
    )
    avg_order_value = serializers.DecimalField(
        max_digits=OrderConstants.MAX_TOTAL_AMOUNT,
        decimal_places=OrderConstants.MAX_DECIMAL_PLACES
    )

    def validate_orders_count(self, value):
        """Метод валидации количества заказов."""
        if value < 0:
            raise serializers.ValidationError(
                'Количество заказов не может быть отрицательным.'
            )
        return value

    def validate_total_revenue(self, value):
        """Метод валидации общей выручки."""
        if value < 0:
            raise serializers.ValidationError(
                'Выручка не может быть отрицательной.'
            )
        return value

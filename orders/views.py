import logging
from typing import Any, Dict

from django.db.models import Avg, Count, Sum
from drf_spectacular.utils import (extend_schema, extend_schema_view,
                                   OpenApiParameter)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import DailyOrderStats, Order, User
from .serializers import (DailyStatsSerializer, OrderUploadSerializer,
                          UserStatsSerializer)

logger = logging.getLogger('orders')


@extend_schema(tags=['Orders'])
@extend_schema_view(
    upload_orders=extend_schema(
        summary='Загрузка заказов',
        description='Загрузка и обновление заказов пользователя',
        auth=[]
    ),
    user_stats=extend_schema(
        summary='Статистика заказов',
        description='Получение статистики по заказам пользователя',
        parameters=[
            OpenApiParameter(
                'user', str, OpenApiParameter.QUERY,
                description='Имя пользователя для статистики',
                required=True
            )
        ],
        auth=[]
    )
)
class OrderUploadStatsViewSet(ViewSet):
    """Представление для загрузки данных о заказах
    и создания статистики заказов по пользователю.
    """

    @action(detail=False, methods=('post',), url_path='upload')
    def upload_orders(self, request):
        """Метод для загрузки данных о заказах."""
        logger.info(
            f'Получен POST запрос на /api/orders/upload от {request.user}.'
        )
        logger.debug(f'Данные запроса: {request.data}')
        serializer = OrderUploadSerializer(data=request.data)
        if serializer.is_valid():
            result: Dict[str, Any] = serializer.save()  # type: ignore
            logger.info('Заказ(ы) успешно сохранены в базу.')
            return Response(
                {'message': 'Заказ(ы) успешно загружены/обновлены.',
                 'statistics': {
                     'created_orders': result['created_orders'],
                     'updated_orders': result['updated_orders'],
                     'created_items': result['created_items'],
                 }},
                status=status.HTTP_201_CREATED
            )
        logger.warning(f'Ошибки валидации: {serializer.errors}.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',), url_path='stats')
    def user_stats(self, request):
        """Метод для создания статистики по пользователю."""
        username = request.query_params.get('user', '').strip()

        logger.info(f'Получен запрос статистики для пользователя: {username}.')

        if not username:
            logger.warning('Запрос статистики без параметра user.')
            route = '/api/orders/stats?user=username'
            return Response(
                {'error': f'Параметр user обязателен. Используйте: {route}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f'Пользователь не найден: {username}.')
            return Response(
                {'error': f'Пользователь {username} не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

        stats = Order.objects.filter(user=user).aggregate(
            orders_count=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount')
        )

        stats_data = {
            'user': username,
            'orders_count': stats['orders_count'] or 0,
            'total_revenue': stats['total_revenue'] or 0,
            'avg_order_value': stats['avg_order_value'] or 0
        }

        serializer = UserStatsSerializer(stats_data)

        logger.info(
            f'Сделана статистика для {username}: '
            f'{stats_data["orders_count"]} заказа(ов), '
            f'общая выручка: {stats_data["total_revenue"]:.2f}, '
            f'средний чек: {stats_data["avg_order_value"]:.2f}.'
        )

        return Response(serializer.data)


class DailyStatsViewSet(ViewSet):
    """ViewSet для просмотра ежедневной статистики."""

    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """Метод для получение ежедневной статистики."""
        stats = DailyOrderStats.objects.all().order_by('-date')[:30]
        serializer = DailyStatsSerializer(stats, many=True)
        return Response(serializer.data)

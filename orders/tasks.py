import logging

from datetime import timedelta

from celery import shared_task
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from .models import User, Order, DailyOrderStats

logger = logging.getLogger('orders')


@shared_task
def daily_order_stats():
    """Метод создания ежедневной задачи для сбора статистики по заказам."""

    stats_date = timezone.now().date() - timedelta(days=1)

    logger.info(f'Начало расчета ежедневной статистики за {stats_date}.')

    try:
        if DailyOrderStats.objects.filter(date=stats_date).exists():
            logger.warning(f'Статистика за {stats_date} уже существует.')
            return f'Статистика за {stats_date} уже существует.'

        yesterday_start = timezone.make_aware(
            timezone.datetime.combine(stats_date, timezone.datetime.min.time())
        )
        yesterday_end = timezone.make_aware(
            timezone.datetime.combine(stats_date, timezone.datetime.max.time())
        )

        orders_stats = Order.objects.filter(
            created_at__range=(yesterday_start, yesterday_end)
        ).aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_order_value=Avg('total_amount')
        )

        active_users_count = User.objects.filter(
            orders__created_at__range=(yesterday_start, yesterday_end)
        ).distinct().count()

        daily_stats = DailyOrderStats.objects.create(
            date=stats_date,
            total_users=active_users_count,
            total_orders=orders_stats['total_orders'] or 0,
            total_revenue=orders_stats['total_revenue'] or 0,
            avg_order_value=orders_stats['avg_order_value'] or 0
        )

        logger.info(
            f'Ежедневная статистика создана за {stats_date}: '
            f'{daily_stats.total_orders} заказов, '
            f'{daily_stats.total_users} пользователей, '
            f'общая выручка: {daily_stats.total_revenue:.2f}.'
        )

        return f'Статистика за {stats_date} успешно создана.'

    except Exception as e:
        logger.error(
            f'Ошибка при расчете статистики за {stats_date}: {str(e)}.'
        )
        raise

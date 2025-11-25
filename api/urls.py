from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import DailyStatsViewSet, OrderUploadStatsViewSet

router = DefaultRouter()

router.register(r'orders', OrderUploadStatsViewSet,
                basename='order-upload-stats')
router.register(r'daily-stats', DailyStatsViewSet,
                basename='daily-stats')


urlpatterns = [
    path('', include(router.urls)),
]

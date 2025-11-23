from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import OrderUploadStatsViewSet

router = DefaultRouter()

router.register(r'orders', OrderUploadStatsViewSet,
                basename='order-upload-stats')


urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter


v1_router = DefaultRouter()

# v1_router.register('access/check', User_s_teamsViewSet,
#                    basename='user_s_teams')

urlpatterns = [
    path('', include(v1_router.urls)),
]

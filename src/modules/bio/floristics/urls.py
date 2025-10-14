from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.floristics.views import (
    FloristicListViewSet,
    FloristicListItemViewSet,
)


router = DefaultRouter()
router.register(r'lists', FloristicListViewSet, basename='floristics-lists')
router.register(r'items', FloristicListItemViewSet, basename='floristics-items')


urlpatterns = [
    path('', include(router.urls)),
]



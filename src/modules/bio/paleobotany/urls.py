from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.paleobotany.views import (
    PollenSampleViewSet,
    PollenImageViewSet,
)


router = DefaultRouter()
router.register(r'samples', PollenSampleViewSet, basename='paleobotany-samples')
router.register(r'images', PollenImageViewSet, basename='paleobotany-images')


urlpatterns = [
    path('', include(router.urls)),
]



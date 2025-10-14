from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.geomorphology.views import (
    SoilProfileViewSet,
    SoilLayerViewSet,
    SoilProfileImageViewSet,
)


router = DefaultRouter()
router.register(r'profiles', SoilProfileViewSet, basename='geomorphology-profiles')
router.register(r'layers', SoilLayerViewSet, basename='geomorphology-layers')
router.register(r'images', SoilProfileImageViewSet, basename='geomorphology-images')


urlpatterns = [
    path('', include(router.urls)),
]



from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.zoology.views import (
    AnimalSpeciesViewSet,
    AnimalPopulationViewSet,
    AnimalObservationViewSet,
)


router = DefaultRouter()
router.register(r'species', AnimalSpeciesViewSet, basename='zoology-species')
router.register(r'populations', AnimalPopulationViewSet, basename='zoology-populations')
router.register(r'observations', AnimalObservationViewSet, basename='zoology-observations')


urlpatterns = [
    path('', include(router.urls)),
]



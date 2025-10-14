from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.successions.views import (
    SuccessionViewSet,
    SuccessionStageViewSet,
    SuccessionSpeciesViewSet,
)


router = DefaultRouter()
router.register(r'successions', SuccessionViewSet, basename='successions')
router.register(r'stages', SuccessionStageViewSet, basename='succession-stages')
router.register(r'stage-species', SuccessionSpeciesViewSet, basename='succession-stage-species')


urlpatterns = [
    path('', include(router.urls)),
]



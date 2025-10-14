from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.interactions.views import SpeciesInteractionViewSet


router = DefaultRouter()
router.register(r'interactions', SpeciesInteractionViewSet, basename='interactions')


urlpatterns = [
    path('', include(router.urls)),
]



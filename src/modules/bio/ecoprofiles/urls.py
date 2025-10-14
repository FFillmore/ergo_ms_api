from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.modules.bio.ecoprofiles.views import (
    EcologicalProfileViewSet,
    ProfileSiteViewSet,
)


router = DefaultRouter()
router.register(r'profiles', EcologicalProfileViewSet, basename='ecoprofiles-profiles')
router.register(r'profile-sites', ProfileSiteViewSet, basename='ecoprofiles-profile-sites')


urlpatterns = [
    path('', include(router.urls)),
]




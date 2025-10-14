from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.ecoprofiles.models import EcologicalProfile, ProfileSite
from src.modules.bio.ecoprofiles.serializers import (
    EcologicalProfileSerializer,
    ProfileSiteSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class EcologicalProfileViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = EcologicalProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return EcologicalProfile.objects.none()
        queryset = EcologicalProfile.objects.filter(user=self.request.user)
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileSiteViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = ProfileSiteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return ProfileSite.objects.none()
        queryset = ProfileSite.objects.filter(profile__user=self.request.user)
        profile_id = self.request.query_params.get('profile_id')
        site_id = self.request.query_params.get('site_id')
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        return queryset




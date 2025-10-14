from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.geomorphology.models import SoilProfile, SoilLayer, SoilProfileImage
from src.modules.bio.geomorphology.serializers import (
    SoilProfileSerializer,
    SoilLayerSerializer,
    SoilProfileImageSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class SoilProfileViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SoilProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SoilProfile.objects.none()
        queryset = SoilProfile.objects.filter(user=self.request.user)
        profile_id = self.request.query_params.get('profile_id')
        site_id = self.request.query_params.get('site_id')
        if profile_id:
            queryset = queryset.filter(profile_id__istartswith=profile_id)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SoilLayerViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SoilLayerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SoilLayer.objects.none()
        queryset = SoilLayer.objects.filter(profile__user=self.request.user)
        profile_pk = self.request.query_params.get('profile_id')
        if profile_pk:
            queryset = queryset.filter(profile_id=profile_pk)
        return queryset


class SoilProfileImageViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SoilProfileImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SoilProfileImage.objects.none()
        queryset = SoilProfileImage.objects.filter(profile__user=self.request.user)
        profile_pk = self.request.query_params.get('profile_id')
        if profile_pk:
            queryset = queryset.filter(profile_id=profile_pk)
        return queryset



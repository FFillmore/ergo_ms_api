from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.paleobotany.models import PollenSample, PollenImage
from src.modules.bio.paleobotany.serializers import (
    PollenSampleSerializer,
    PollenImageSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class PollenSampleViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = PollenSampleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return PollenSample.objects.none()
        queryset = PollenSample.objects.filter(user=self.request.user)
        sample_id = self.request.query_params.get('sample_id')
        if sample_id:
            queryset = queryset.filter(sample_id__istartswith=sample_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PollenImageViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = PollenImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return PollenImage.objects.none()
        queryset = PollenImage.objects.filter(sample__user=self.request.user)
        sample_pk = self.request.query_params.get('sample_id')
        if sample_pk:
            queryset = queryset.filter(sample_id=sample_pk)
        return queryset



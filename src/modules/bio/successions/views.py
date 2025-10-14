from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.successions.models import Succession, SuccessionStage, SuccessionSpecies
from src.modules.bio.successions.serializers import (
    SuccessionSerializer,
    SuccessionStageSerializer,
    SuccessionSpeciesSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class SuccessionViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SuccessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Succession.objects.none()
        queryset = Succession.objects.filter(user=self.request.user)
        site_id = self.request.query_params.get('site_id')
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuccessionStageViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SuccessionStageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SuccessionStage.objects.none()
        queryset = SuccessionStage.objects.filter(succession__user=self.request.user)
        succession_id = self.request.query_params.get('succession_id')
        if succession_id:
            queryset = queryset.filter(succession_id=succession_id)
        return queryset


class SuccessionSpeciesViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SuccessionSpeciesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SuccessionSpecies.objects.none()
        queryset = SuccessionSpecies.objects.filter(stage__succession__user=self.request.user)
        stage_id = self.request.query_params.get('stage_id')
        plant_species_id = self.request.query_params.get('plant_species_id')
        if stage_id:
            queryset = queryset.filter(stage_id=stage_id)
        if plant_species_id:
            queryset = queryset.filter(plant_species_id=plant_species_id)
        return queryset



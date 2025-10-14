from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.interactions.models import SpeciesInteraction
from src.modules.bio.interactions.serializers import SpeciesInteractionSerializer
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class SpeciesInteractionViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SpeciesInteractionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return SpeciesInteraction.objects.none()
        queryset = SpeciesInteraction.objects.filter(user=self.request.user)
        plant_species_id = self.request.query_params.get('plant_species_id')
        animal_species_id = self.request.query_params.get('animal_species_id')
        site_id = self.request.query_params.get('site_id')
        interaction_type = self.request.query_params.get('interaction_type')
        if plant_species_id:
            queryset = queryset.filter(plant_species_id=plant_species_id)
        if animal_species_id:
            queryset = queryset.filter(animal_species_id=animal_species_id)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



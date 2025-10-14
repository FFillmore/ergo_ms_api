from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.zoology.models import (
    AnimalSpecies,
    AnimalPopulation,
    AnimalObservation,
)
from src.modules.bio.zoology.serializers import (
    AnimalSpeciesSerializer,
    AnimalPopulationSerializer,
    AnimalObservationSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class AnimalSpeciesViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    queryset = AnimalSpecies.objects.all()
    serializer_class = AnimalSpeciesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return AnimalSpecies.objects.none()
        queryset = super().get_queryset()
        latin_name = self.request.query_params.get('latin_name')
        author = self.request.query_params.get('author')
        title = self.request.query_params.get('title')

        if latin_name:
            queryset = queryset.filter(latin_name__istartswith=latin_name)
        if author:
            queryset = queryset.filter(author__istartswith=author)
        if title:
            queryset = queryset.filter(title__istartswith=title)

        return queryset


class AnimalPopulationViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = AnimalPopulationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return AnimalPopulation.objects.none()
        queryset = AnimalPopulation.objects.filter(user=self.request.user)
        animal_species_id = self.request.query_params.get('animal_species_id')
        site_id = self.request.query_params.get('site_id')
        if animal_species_id:
            queryset = queryset.filter(animal_species_id=animal_species_id)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnimalObservationViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = AnimalObservationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return AnimalObservation.objects.none()
        queryset = AnimalObservation.objects.filter(user=self.request.user)
        animal_species_id = self.request.query_params.get('animal_species_id')
        site_id = self.request.query_params.get('site_id')
        population_id = self.request.query_params.get('population_id')
        if animal_species_id:
            queryset = queryset.filter(animal_species_id=animal_species_id)
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if population_id:
            queryset = queryset.filter(population_id=population_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



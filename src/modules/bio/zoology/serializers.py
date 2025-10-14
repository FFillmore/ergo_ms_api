from rest_framework.serializers import ModelSerializer

from src.modules.bio.zoology.models import (
    AnimalSpecies,
    AnimalPopulation,
    AnimalObservation,
)


class AnimalSpeciesSerializer(ModelSerializer):
    class Meta:
        model = AnimalSpecies
        fields = '__all__'
        read_only_fields = ['species_id']


class AnimalPopulationSerializer(ModelSerializer):
    class Meta:
        model = AnimalPopulation
        fields = '__all__'
        read_only_fields = ['id', 'user']


class AnimalObservationSerializer(ModelSerializer):
    class Meta:
        model = AnimalObservation
        fields = '__all__'
        read_only_fields = ['id', 'user']



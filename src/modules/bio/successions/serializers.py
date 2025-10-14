from rest_framework.serializers import ModelSerializer

from src.modules.bio.successions.models import Succession, SuccessionStage, SuccessionSpecies


class SuccessionSerializer(ModelSerializer):
    class Meta:
        model = Succession
        fields = '__all__'
        read_only_fields = ['id', 'user']


class SuccessionStageSerializer(ModelSerializer):
    class Meta:
        model = SuccessionStage
        fields = '__all__'
        read_only_fields = ['id']


class SuccessionSpeciesSerializer(ModelSerializer):
    class Meta:
        model = SuccessionSpecies
        fields = '__all__'
        read_only_fields = ['id']



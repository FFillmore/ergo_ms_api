from rest_framework.serializers import ModelSerializer

from src.modules.bio.interactions.models import SpeciesInteraction


class SpeciesInteractionSerializer(ModelSerializer):
    class Meta:
        model = SpeciesInteraction
        fields = '__all__'
        read_only_fields = ['id', 'user']



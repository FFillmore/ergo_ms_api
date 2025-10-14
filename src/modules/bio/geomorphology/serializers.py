from rest_framework.serializers import ModelSerializer

from src.modules.bio.geomorphology.models import SoilProfile, SoilLayer, SoilProfileImage


class SoilProfileSerializer(ModelSerializer):
    class Meta:
        model = SoilProfile
        fields = '__all__'
        read_only_fields = ['id', 'user']


class SoilLayerSerializer(ModelSerializer):
    class Meta:
        model = SoilLayer
        fields = '__all__'
        read_only_fields = ['id']


class SoilProfileImageSerializer(ModelSerializer):
    class Meta:
        model = SoilProfileImage
        fields = '__all__'
        read_only_fields = ['id']



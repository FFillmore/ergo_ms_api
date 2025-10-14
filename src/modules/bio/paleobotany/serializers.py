from rest_framework.serializers import ModelSerializer

from src.modules.bio.paleobotany.models import PollenSample, PollenImage


class PollenSampleSerializer(ModelSerializer):
    class Meta:
        model = PollenSample
        fields = '__all__'
        read_only_fields = ['id', 'user']


class PollenImageSerializer(ModelSerializer):
    class Meta:
        model = PollenImage
        fields = '__all__'
        read_only_fields = ['id']



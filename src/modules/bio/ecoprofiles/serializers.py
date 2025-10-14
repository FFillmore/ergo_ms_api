from rest_framework.serializers import ModelSerializer

from src.modules.bio.ecoprofiles.models import EcologicalProfile, ProfileSite


class EcologicalProfileSerializer(ModelSerializer):
    class Meta:
        model = EcologicalProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_date']


class ProfileSiteSerializer(ModelSerializer):
    class Meta:
        model = ProfileSite
        fields = '__all__'
        read_only_fields = ['id']




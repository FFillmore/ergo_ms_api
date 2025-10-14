from rest_framework.serializers import ModelSerializer

from src.modules.bio.floristics.models import FloristicList, FloristicListItem


class FloristicListSerializer(ModelSerializer):
    class Meta:
        model = FloristicList
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class FloristicListItemSerializer(ModelSerializer):
    class Meta:
        model = FloristicListItem
        fields = '__all__'
        read_only_fields = ['id']



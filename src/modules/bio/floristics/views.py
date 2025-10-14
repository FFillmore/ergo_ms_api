from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.floristics.models import FloristicList, FloristicListItem
from src.modules.bio.floristics.serializers import (
    FloristicListSerializer,
    FloristicListItemSerializer,
)
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class FloristicListViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = FloristicListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return FloristicList.objects.none()
        queryset = FloristicList.objects.filter(user=self.request.user)
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FloristicListItemViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = FloristicListItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return FloristicListItem.objects.none()
        queryset = FloristicListItem.objects.filter(list__user=self.request.user)
        list_id = self.request.query_params.get('list_id')
        species_id = self.request.query_params.get('species_id')
        if list_id:
            queryset = queryset.filter(list_id=list_id)
        if species_id:
            queryset = queryset.filter(species_id=species_id)
        return queryset



from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from src.modules.bio.models import Species
from src.modules.bio.serializers import SpeciesSerializer
from src.modules.bio.views.base import StandardResultsSetPagination


class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.query_params.get('title')
        author = self.request.query_params.get('author')

        if title:
            queryset = queryset.filter(title__istartswith=title)

        if author:
            queryset = queryset.filter(author__istartswith=author)

        return queryset



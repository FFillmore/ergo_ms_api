from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ValidationError

from src.modules.bio.geobotany.models import Site, Description


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class BaseDescriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def validate_site_params(self, site_number, zone_type=None):
        if zone_type:
            valid_zone_types = [choice[0] for choice in Site._meta.get_field('zone_type').choices]
            if zone_type not in valid_zone_types:
                raise ValidationError({"error": f"Недопустимый zone_type. Должно быть одно из: {valid_zone_types}"})
        return True

    def get_site(self, site_number, zone_type):
        self.validate_site_params(site_number, zone_type)
        try:
            return Site.objects.get(
                user=self.request.user,
                site_number=site_number,
                zone_type=zone_type,
            )
        except Site.DoesNotExist:
            return None

    def prepare_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"error": message}, status=status_code)

    def prepare_not_found_response(self, entity_type="Данные", status_code=status.HTTP_404_NOT_FOUND):
        return Response({"message": f"{entity_type} не найдены"}, status=status_code)


class BaseSiteAnalyticsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def validate_site_params(self, site_number, zone_type):
        valid_zone_types = [choice[0] for choice in Site._meta.get_field('zone_type').choices]
        if zone_type not in valid_zone_types:
            raise ValidationError({"error": f"Недопустимый zone_type. Должно быть одно из: {valid_zone_types}"})
        return True

    def get_site_data(self, user, site_number, zone_type):
        from src.modules.bio.methods import get_species_data_from_site

        self.validate_site_params(site_number, zone_type)
        data = get_species_data_from_site(user, site_number, zone_type)
        if data.empty:
            return None
        return data

    def prepare_error_response(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"error": message}, status=status_code)

    def prepare_not_found_response(self, entity_type="Данные"):
        return Response({"message": f"{entity_type} не найдены"}, status=status.HTTP_404_NOT_FOUND)




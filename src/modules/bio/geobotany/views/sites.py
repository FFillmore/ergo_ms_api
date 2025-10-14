from django.http import Http404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from src.modules.bio.geobotany.models import Site, Description
from src.modules.bio.serializers import SiteSerializer
from src.modules.bio.views.base import StandardResultsSetPagination
from src.core.utils.mixins import SwaggerSafeMixin


class SiteViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def validate_zone_type(self, zone_type):
        valid_zone_types = [choice[0] for choice in Site._meta.get_field('zone_type').choices]
        if zone_type not in valid_zone_types:
            raise ValidationError({"error": f"Недопустимый zone_type. Должно быть одно из: {valid_zone_types}"})

    def get_object(self):
        site_number = self.kwargs.get('site_number')
        zone_type = self.kwargs.get('zone_type')

        if not site_number or not zone_type:
            return super().get_object()

        self.validate_zone_type(zone_type)
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(site_number=site_number, zone_type=zone_type).first()

        if not obj:
            raise Http404(f"Площадка с site_number={site_number} и zone_type={zone_type} не найдена")

        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        operation_description="Получить список всех площадок пользователя",
        responses={
            200: SiteSerializer(many=True),
            401: "Не авторизован",
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Количество элементов на странице", type=openapi.TYPE_INTEGER),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новую площадку",
        request_body=SiteSerializer,
        responses={201: SiteSerializer(), 400: "Неверные данные", 401: "Не авторизован"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получить информацию о площадке",
        responses={200: SiteSerializer(), 404: "Площадка не найдена", 401: "Не авторизован"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Полностью обновить площадку",
        request_body=SiteSerializer,
        responses={200: SiteSerializer(), 400: "Неверные данные", 401: "Не авторизован", 404: "Площадка не найдена"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частично обновить площадку",
        request_body=SiteSerializer,
        responses={200: SiteSerializer(), 400: "Неверные данные", 401: "Не авторизован", 404: "Площадка не найдена"},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удалить площадку",
        responses={200: "Площадка удалена", 401: "Не авторизован", 404: "Площадка не найдена"},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Площадка удалена"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        base = Site.objects.filter(user=self.get_safe_user())
        queryset = self.get_safe_queryset(base)
        if self.is_swagger_fake_view():
            return queryset

        zone_type = self.kwargs.get('zone_type')
        if zone_type:
            self.validate_zone_type(zone_type)
            queryset = queryset.filter(zone_type=zone_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SiteBulkDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Массовое удаление площадок по списку ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description="Список ID площадок для удаления"),
            },
            required=['ids'],
        ),
        responses={
            200: openapi.Response(
                description="Площадки удалены",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'message': openapi.Schema(type=openapi.TYPE_STRING), 'count': openapi.Schema(type=openapi.TYPE_INTEGER)},
                ),
            ),
            400: "Некорректные данные",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({"error": "Поле 'ids' должно быть списком"}, status=status.HTTP_400_BAD_REQUEST)

        sites = Site.objects.filter(id__in=ids, user=request.user)
        count = sites.count()

        with transaction.atomic():
            Description.objects.filter(site__in=sites).delete()
            sites.delete()

        return Response({"message": f"Удалено площадок: {count}", "count": count}, status=status.HTTP_200_OK)



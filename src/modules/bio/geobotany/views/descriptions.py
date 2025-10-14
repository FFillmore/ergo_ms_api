from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from src.modules.bio.geobotany.models import Description, Site
from src.modules.bio.serializers import DescriptionSerializer, DescriptionCreateSerializer
from src.modules.bio.geobotany.views.base import BaseDescriptionView
from src.core.utils.mixins import SwaggerSafeMixin


class DescriptionView(BaseDescriptionView):
    serializer_class = DescriptionSerializer

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Description.objects.none()

        site_number = self.kwargs['site_number']
        zone_type = self.kwargs['zone_type']
        self.validate_site_params(site_number, zone_type)

        site = self.get_site(site_number, zone_type)
        if site is None:
            return Description.objects.none()

        return (
            Description.objects.filter(user=self.get_safe_user(), site=site)
            .select_related('species', 'site')
        )

    @swagger_auto_schema(
        operation_description="Получить описания на площадке",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        responses={200: DescriptionSerializer(many=True), 404: "Описания не найдены", 401: "Не авторизован"},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return self.prepare_not_found_response("Описания")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Добавить описания (одно или несколько) на площадку",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида', example='Species Name'),
                    'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида', example='Author Name'),
                    'tier': openapi.Schema(type=openapi.TYPE_STRING, enum=['', 'A', 'B', 'C', 'D'], description='Ярус', example='A'),
                    'abundance': openapi.Schema(type=openapi.TYPE_STRING, enum=['r', '+', '1', '2', '3', '4', '5'], description='Балл обилия', example='1'),
                },
                required=['title', 'author', 'tier', 'abundance'],
            ),
            description='Список описаний для создания',
        ),
        responses={201: DescriptionSerializer(many=True), 400: 'Некорректные данные', 404: 'Площадка не найдена', 401: "Не авторизован"},
    )
    def post(self, request, site_number, zone_type):
        descriptions_data = request.data
        if not isinstance(descriptions_data, list):
            return self.prepare_error_response("Ожидается список описаний")

        site = self.get_site(site_number, zone_type)
        if site is None:
            return self.prepare_not_found_response(f"Площадка с site_number {site_number} и zone_type {zone_type}")

        serializer = DescriptionCreateSerializer(data=descriptions_data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            descriptions = [
                Description(
                    user=request.user,
                    site=site,
                    species=desc['species'],
                    tier=desc['tier'],
                    abundance=desc['abundance'],
                )
                for desc in serializer.validated_data
            ]
            Description.objects.bulk_create(descriptions)

        created_descriptions = Description.objects.filter(site=site).select_related('species', 'site')
        output_serializer = DescriptionSerializer(created_descriptions, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Исправить все описания на площадке",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида', example='Species Name'),
                    'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида', example='Author Name'),
                    'tier': openapi.Schema(type=openapi.TYPE_STRING, enum=['', 'A', 'B', 'C', 'D'], description='Ярус', example='A'),
                    'abundance': openapi.Schema(type=openapi.TYPE_STRING, enum=['r', '+', '1', '2', '3', '4', '5'], description='Балл обилия', example='1'),
                },
                required=['title', 'author', 'tier', 'abundance'],
            ),
            description='Список описаний для создания',
        ),
        responses={200: DescriptionSerializer(many=True), 400: 'Некорректные данные', 404: 'Площадка не найдена', 401: "Не авторизован"},
    )
    def put(self, request, site_number, zone_type):
        descriptions_data = request.data
        if not isinstance(descriptions_data, list):
            return self.prepare_error_response("Ожидается список описаний")

        site = self.get_site(site_number, zone_type)
        if site is None:
            return self.prepare_not_found_response(f"Площадка с site_number {site_number} и zone_type {zone_type}")

        with transaction.atomic():
            Description.objects.filter(site=site).delete()
            serializer = DescriptionCreateSerializer(data=descriptions_data, many=True)
            serializer.is_valid(raise_exception=True)
            descriptions = [
                Description(
                    user=request.user,
                    site=site,
                    species=desc['species'],
                    tier=desc['tier'],
                    abundance=desc['abundance'],
                )
                for desc in serializer.validated_data
            ]
            Description.objects.bulk_create(descriptions)

        updated_descriptions = Description.objects.filter(site=site).select_related('species', 'site')
        output_serializer = DescriptionSerializer(updated_descriptions, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Частично обновить описания на площадке",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида', example='Species Name'),
                    'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида', example='Author Name'),
                    'tier': openapi.Schema(type=openapi.TYPE_STRING, enum=['', 'A', 'B', 'C', 'D'], description='Ярус', example='A'),
                    'abundance': openapi.Schema(type=openapi.TYPE_STRING, enum=['r', '+', '1', '2', '3', '4', '5'], description='Балл обилия', example='1'),
                },
                required=['title', 'author', 'tier', 'abundance'],
            ),
            description='Список описаний для создания',
        ),
        responses={200: DescriptionSerializer(many=True), 400: 'Некорректные данные', 404: 'Площадка не найдена', 401: "Не авторизован"},
    )
    def patch(self, request, site_number, zone_type):
        descriptions_data = request.data
        if not isinstance(descriptions_data, list):
            return self.prepare_error_response("Ожидается список описаний")

        site = self.get_site(site_number, zone_type)
        if site is None:
            return self.prepare_not_found_response(f"Площадка с site_number {site_number} и zone_type {zone_type}")

        serializer = DescriptionCreateSerializer(data=descriptions_data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for desc_data in serializer.validated_data:
                species = desc_data['species']
                tier = desc_data['tier']
                description, created = Description.objects.get_or_create(
                    user=request.user,
                    site=site,
                    species=species,
                    tier=tier,
                    defaults={'abundance': desc_data['abundance']},
                )
                if not created:
                    description.abundance = desc_data['abundance']
                    description.save()

        updated_descriptions = Description.objects.filter(site=site).select_related('species', 'site')
        output_serializer = DescriptionSerializer(updated_descriptions, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Удалить все описания на площадке",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        responses={200: "Описания удалены", 404: "Описания не найдены", 401: "Не авторизован"},
    )
    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return self.prepare_not_found_response("Описания")
        queryset.delete()
        return Response({"message": "Описания удалены"}, status=status.HTTP_200_OK)


class DescriptionDetailView(BaseDescriptionView):
    serializer_class = DescriptionSerializer

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Description.objects.none()

        description_id = self.kwargs['description_id']
        return Description.objects.filter(id=description_id, user=self.get_safe_user()).select_related('species', 'site')

    @swagger_auto_schema(
        operation_description="Удалить конкретное описание по ID",
        responses={200: "Описание удалено", 404: "Описание не найдено", 401: "Не авторизован"},
    )
    def delete(self, request, description_id, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return self.prepare_not_found_response("Описание")
        queryset.delete()
        return Response({"message": "Описание удалено"}, status=status.HTTP_200_OK)


class DescriptionBulkDeleteView(BaseDescriptionView):
    @swagger_auto_schema(
        operation_description="Массовое удаление описаний по списку ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description="Список ID описаний для удаления"),
            },
            required=['ids'],
        ),
        responses={
            200: openapi.Response(
                description="Описания удалены",
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
            return self.prepare_error_response("Поле 'ids' должно быть списком")

        descriptions = Description.objects.filter(id__in=ids, user=request.user)
        count = descriptions.count()

        with transaction.atomic():
            descriptions.delete()

        return Response({"message": f"Удалено описаний: {count}", "count": count}, status=status.HTTP_200_OK)



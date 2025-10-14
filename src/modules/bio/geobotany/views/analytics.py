from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from src.modules.bio.constants import SCALES_DICT, SUPPORTED_SPECTRUM_TYPES
from src.modules.bio.geobotany.models import Site
from src.modules.bio.methods import (
    calculate_means,
    calculate_spectrums_percentage_distribution,
    get_comparison_data,
    analyze_custom_data,
    get_species_data_by_custom_data,
)
from src.modules.bio.geobotany.views.base import BaseSiteAnalyticsView


class SiteMeansView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить данные о средних значениях шкал для площадки",
        manual_parameters=[
            openapi.Parameter('site_number', openapi.IN_PATH, description="Номер площадки", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('scale_type', openapi.IN_QUERY, description="Тип шкалы", type=openapi.TYPE_STRING, required=True, enum=list(SCALES_DICT.keys())),
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        responses={
            200: openapi.Response(
                'Данные средних значений',
                openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'scale': openapi.Schema(type=openapi.TYPE_STRING), 'value': openapi.Schema(type=openapi.TYPE_NUMBER)}))}),
            ),
            400: 'Недопустимые параметры',
            404: 'Площадка или данные не найдены',
            401: "Не авторизован",
        },
    )
    def get(self, request, site_number, zone_type):
        scale_type = request.query_params.get('scale_type')
        if not scale_type:
            return self.prepare_error_response("Параметр scale_type обязателен")
        if scale_type not in SCALES_DICT:
            return self.prepare_error_response(f"Недопустимый scale_type: {scale_type}")

        data = self.get_site_data(request.user, site_number, zone_type)
        if data is None:
            return self.prepare_not_found_response("Данные о растениях для этой площадки")

        means_df = calculate_means(data, scale_type)
        if means_df is None:
            return self.prepare_not_found_response("Данные для вычисления средних значений")

        result_data = means_df.to_dict(orient='records')
        return Response({'data': result_data}, status=status.HTTP_200_OK)


class CustomSiteMeansView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить данные о средних значениях шкал для площадки на основе пользовательских данных",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'scale_type': openapi.Schema(type=openapi.TYPE_STRING, enum=list(SCALES_DICT.keys()), description="Тип шкалы (ellenberg, landolt, tsyganov)"),
                'custom_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'descriptions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида'), 'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида'), 'abundance': openapi.Schema(type=openapi.TYPE_STRING, description='Балл обилия')}, required=['title', 'author', 'abundance']), description='Список описаний видов на площадке'),
                        'metadata': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'site_number': openapi.Schema(type=openapi.TYPE_STRING), 'zone_type': openapi.Schema(type=openapi.TYPE_STRING)}, description='Метаданные площадки'),
                    },
                    description="Пользовательские данные по площадке",
                ),
            },
            required=['scale_type', 'custom_data'],
        ),
        responses={
            200: openapi.Response('Данные средних значений', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'scale': openapi.Schema(type=openapi.TYPE_STRING), 'value': openapi.Schema(type=openapi.TYPE_NUMBER)}))})),
            400: "Неверные параметры",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        scale_type = request.data.get('scale_type')
        custom_data = request.data.get('custom_data', {})
        if not scale_type:
            return self.prepare_error_response("Необходимо указать тип шкалы (scale_type)")
        if scale_type not in SCALES_DICT:
            return self.prepare_error_response(f"Неверный тип шкалы: {scale_type}. Доступные типы: {', '.join(SCALES_DICT.keys())}")

        descriptions = custom_data.get('descriptions', [])
        if not descriptions:
            return self.prepare_error_response("Необходимо предоставить данные о видах в поле custom_data.descriptions")

        site_df = get_species_data_by_custom_data(descriptions, scale_type)
        if site_df is None:
            return self.prepare_error_response("Не удалось найти соответствующие виды в базе данных")

        means_df = calculate_means(site_df, scale_type)
        if means_df is None:
            return self.prepare_error_response("Не удалось вычислить средние значения шкал")

        result_data = means_df.to_dict(orient='records')
        return Response({'data': result_data}, status=status.HTTP_200_OK)


class SiteDistributionView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить данные о процентном распределении выбранного спектра для площадки",
        manual_parameters=[
            openapi.Parameter('spectrum_type', openapi.IN_QUERY, description="Тип спектра", type=openapi.TYPE_STRING, required=True, enum=SUPPORTED_SPECTRUM_TYPES),
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        responses={
            200: openapi.Response('Данные распределения', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'scale': openapi.Schema(type=openapi.TYPE_STRING), 'value': openapi.Schema(type=openapi.TYPE_NUMBER)}))})),
            400: 'Недопустимые параметры',
            404: 'Площадка или данные не найдены',
            401: "Не авторизован",
        },
    )
    def get(self, request, site_number, zone_type):
        spectrum_type = request.query_params.get('spectrum_type')
        if not spectrum_type:
            return self.prepare_error_response("Параметр spectrum_type обязателен")
        if spectrum_type not in SUPPORTED_SPECTRUM_TYPES:
            return self.prepare_error_response(f"Недопустимый spectrum_type: {spectrum_type}. Должен быть один из: {SUPPORTED_SPECTRUM_TYPES}")

        data = self.get_site_data(request.user, site_number, zone_type)
        if data is None:
            return self.prepare_not_found_response("Данные о растениях для этой площадки")
        if spectrum_type not in data.columns:
            return self.prepare_error_response(f"Спектр {spectrum_type} отсутствует в данных")

        distribution_df = calculate_spectrums_percentage_distribution(data, spectrum_type)
        if distribution_df is None:
            return self.prepare_not_found_response(f"Данные для вычисления распределения спектра {spectrum_type}")

        result_data = distribution_df.to_dict(orient='records')
        return Response({'data': result_data}, status=status.HTTP_200_OK)


class CustomSiteDistributionView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить данные о процентном распределении выбранного спектра для площадки на основе пользовательских данных",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'spectrum_type': openapi.Schema(type=openapi.TYPE_STRING, enum=SUPPORTED_SPECTRUM_TYPES, description="Тип спектра (raunkiaer, serebryakov, ecobiomorphs, geoelements, ta)"),
                'custom_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'descriptions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида'), 'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида'), 'abundance': openapi.Schema(type=openapi.TYPE_STRING, description='Балл обилия')}, required=['title', 'author', 'abundance']), description='Список описаний видов на площадке'),
                        'metadata': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'site_number': openapi.Schema(type=openapi.TYPE_STRING), 'zone_type': openapi.Schema(type=openapi.TYPE_STRING)}, description='Метаданные площадки'),
                    },
                    description="Пользовательские данные по площадке",
                ),
            },
            required=['spectrum_type', 'custom_data'],
        ),
        responses={
            200: openapi.Response('Данные распределения', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'scale': openapi.Schema(type=openapi.TYPE_STRING), 'value': openapi.Schema(type=openapi.TYPE_NUMBER)}))})),
            400: "Неверные параметры",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        spectrum_type = request.data.get('spectrum_type')
        custom_data = request.data.get('custom_data', {})
        if not spectrum_type:
            return self.prepare_error_response("Необходимо указать тип спектра (spectrum_type)")
        if spectrum_type not in SUPPORTED_SPECTRUM_TYPES:
            return self.prepare_error_response(f"Недопустимый spectrum_type: {spectrum_type}. Должен быть один из: {SUPPORTED_SPECTRUM_TYPES}")

        descriptions = custom_data.get('descriptions', [])
        if not descriptions:
            return self.prepare_error_response("Необходимо предоставить данные о видах в поле custom_data.descriptions")

        site_df = get_species_data_by_custom_data(descriptions)
        if site_df is None:
            return self.prepare_error_response("Не удалось найти соответствующие виды в базе данных")
        if spectrum_type not in site_df.columns:
            return self.prepare_error_response(f"Спектр {spectrum_type} отсутствует в данных")

        distribution_df = calculate_spectrums_percentage_distribution(site_df, spectrum_type)
        if distribution_df is None:
            return self.prepare_error_response(f"Не удалось вычислить распределение спектра {spectrum_type}")

        result_data = distribution_df.to_dict(orient='records')
        return Response({'data': result_data}, status=status.HTTP_200_OK)


class SiteClassificationView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить классификацию ассоциаций для площадки на основе машинного обучения",
        manual_parameters=[
            openapi.Parameter('zone_type', openapi.IN_PATH, description="Тип местности", type=openapi.TYPE_STRING, required=True, enum=[choice[0] for choice in Site._meta.get_field('zone_type').choices]),
        ],
        responses={
            200: openapi.Response('Результаты классификации', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'association': openapi.Schema(type=openapi.TYPE_STRING), 'sub_element': openapi.Schema(type=openapi.TYPE_STRING), 'confidence': openapi.Schema(type=openapi.TYPE_STRING), 'confidence_value': openapi.Schema(type=openapi.TYPE_NUMBER)})), 'meta': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'title': openapi.Schema(type=openapi.TYPE_STRING), 'zone_type': openapi.Schema(type=openapi.TYPE_STRING)})})),
            400: 'Недопустимые параметры',
            404: 'Площадка, данные или модель не найдены',
            401: "Не авторизован",
        },
    )
    def get(self, request, site_number, zone_type):
        self.validate_site_params(site_number, zone_type)
        try:
            from src.modules.bio.ml.model_loader import get_model
            model = get_model(zone_type)
        except ValueError as e:
            return self.prepare_error_response(str(e))
        except Exception as e:
            return self.prepare_error_response(f"Ошибка загрузки модели: {str(e)}")

        data = self.get_site_data(request.user, site_number, zone_type)
        if data is None:
            return self.prepare_not_found_response("Данные о растениях для этой площадки")

        required_columns = ['title', 'abundance_numeric']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return self.prepare_error_response(f"В данных отсутствуют столбцы: {', '.join(missing_columns)}")

        try:
            pivot_data = data.pivot_table(index=lambda _: '1', columns='title', values='abundance_numeric', aggfunc='first').fillna(0)
            pivot_data = pivot_data.reindex(columns=model.feature_names_in_, fill_value=0)
            probabilities = model.predict_proba(pivot_data)
            associations = model.classes_

            association_proba = [(associations[i], proba) for i, proba in enumerate(probabilities[0]) if proba > 0]
            sorted_association_proba = sorted(association_proba, key=lambda x: x[1], reverse=True)

            result_data = []
            for assoc, proba in sorted_association_proba:
                parts = assoc.split("_")
                association = parts[0] if len(parts) > 0 else assoc
                sub_element = parts[1] if len(parts) > 1 else ""
                result_data.append({"association": association, "sub_element": sub_element, "confidence": f"{proba * 100:.2f}%", "confidence_value": round(proba * 100, 2)})

            return Response({'data': result_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return self.prepare_error_response(f"Ошибка при классификации данных: {str(e)}")


class CustomSiteClassificationView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить классификацию ассоциаций для площадки на основе пользовательских данных",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'custom_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'descriptions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название вида'), 'author': openapi.Schema(type=openapi.TYPE_STRING, description='Автор вида'), 'abundance': openapi.Schema(type=openapi.TYPE_STRING, description='Балл обилия')}, required=['title', 'author', 'abundance']), description='Список описаний видов на площадке'),
                        'metadata': openapi.Schema(type=openapi.TYPE_OBJECT, properties={'site_number': openapi.Schema(type=openapi.TYPE_STRING), 'zone_type': openapi.Schema(type=openapi.TYPE_STRING, description="Тип местности, используется для выбора соответствующей модели классификации")}, required=['zone_type'], description='Метаданные площадки'),
                    },
                    description="Пользовательские данные по площадке",
                ),
            },
            required=['custom_data'],
        ),
        responses={
            200: openapi.Response('Результаты классификации', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'association': openapi.Schema(type=openapi.TYPE_STRING), 'sub_element': openapi.Schema(type=openapi.TYPE_STRING), 'confidence': openapi.Schema(type=openapi.TYPE_STRING), 'confidence_value': openapi.Schema(type=openapi.TYPE_NUMBER)}))})),
            400: "Неверные параметры",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        custom_data = request.data.get('custom_data', {})
        if not custom_data:
            return self.prepare_error_response("Необходимо предоставить данные в поле custom_data")

        descriptions = custom_data.get('descriptions', [])
        if not descriptions:
            return self.prepare_error_response("Необходимо предоставить данные о видах в поле custom_data.descriptions")

        metadata = custom_data.get('metadata', {})
        zone_type = metadata.get('zone_type')
        if not zone_type:
            return self.prepare_error_response("Необходимо указать тип местности в поле custom_data.metadata.zone_type")

        valid_zone_types = [choice[0] for choice in Site._meta.get_field('zone_type').choices]
        if zone_type not in valid_zone_types:
            return self.prepare_error_response(f"Недопустимый zone_type: {zone_type}. Должен быть один из: {valid_zone_types}")

        try:
            from src.modules.bio.ml.model_loader import get_model
            model = get_model(zone_type)
        except ValueError as e:
            return self.prepare_error_response(str(e))
        except Exception as e:
            return self.prepare_error_response(f"Ошибка загрузки модели: {str(e)}")

        site_df = get_species_data_by_custom_data(descriptions)
        if site_df is None:
            return self.prepare_error_response("Не удалось найти соответствующие виды в базе данных")

        required_columns = ['title', 'abundance_numeric']
        missing_columns = [col for col in required_columns if col not in site_df.columns]
        if missing_columns:
            return self.prepare_error_response(f"В данных отсутствуют столбцы: {', '.join(missing_columns)}")

        try:
            pivot_data = site_df.pivot_table(index=lambda _: '1', columns='title', values='abundance_numeric', aggfunc='first').fillna(0)
            pivot_data = pivot_data.reindex(columns=model.feature_names_in_, fill_value=0)
            probabilities = model.predict_proba(pivot_data)
            associations = model.classes_

            association_proba = [(associations[i], proba) for i, proba in enumerate(probabilities[0]) if proba > 0]
            sorted_association_proba = sorted(association_proba, key=lambda x: x[1], reverse=True)

            result_data = []
            for assoc, proba in sorted_association_proba:
                parts = assoc.split("_")
                association = parts[0] if len(parts) > 0 else assoc
                sub_element = parts[1] if len(parts) > 1 else ""
                result_data.append({"association": association, "sub_element": sub_element, "confidence": f"{proba * 100:.2f}%", "confidence_value": round(proba * 100, 2)})

            return Response({'data': result_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return self.prepare_error_response(f"Ошибка при классификации данных: {str(e)}")


class SiteComparisonView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Получить данные для сравнения нескольких площадок по выбранным элементам",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'site_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description="Список ID площадок для сравнения"),
                'elements': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING, enum=SUPPORTED_SPECTRUM_TYPES + list(SCALES_DICT.keys())), description="Список элементов для сравнения (raunkiaer, serebryakov, ecobiomorphs, geoelements, ta, ellenberg, landolt, tsyganov)"),
            },
            required=['site_ids', 'elements'],
        ),
        responses={
            200: openapi.Response(description="Данные для сравнения площадок", schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_OBJECT)})),
            400: "Неверные параметры",
            404: "Данные не найдены",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        site_ids = request.data.get('site_ids', [])
        elements = request.data.get('elements', [])
        if not site_ids:
            return self.prepare_error_response("Необходимо указать хотя бы одну площадку")
        if not elements:
            return self.prepare_error_response("Необходимо указать хотя бы один элемент для сравнения")

        valid_elements = SUPPORTED_SPECTRUM_TYPES + list(SCALES_DICT.keys())
        invalid_elements = [elem for elem in elements if elem not in valid_elements]
        if invalid_elements:
            return self.prepare_error_response(f"Неверные элементы: {', '.join(invalid_elements)}. Доступные элементы: {', '.join(valid_elements)}")

        comparison_data = get_comparison_data(request.user, site_ids, elements)
        if not comparison_data:
            return self.prepare_not_found_response("Данные для сравнения площадок")

        return Response({'data': comparison_data}, status=status.HTTP_200_OK)


class SiteCustomAnalysisView(BaseSiteAnalyticsView):
    @swagger_auto_schema(
        operation_description="Анализ пользовательских данных для сравнения площадок",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'elements': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING, enum=SUPPORTED_SPECTRUM_TYPES + list(SCALES_DICT.keys())), description="Список элементов для сравнения (raunkiaer, serebryakov, ecobiomorphs, geoelements, ta, ellenberg, landolt, tsyganov)"),
                'custom_data': openapi.Schema(type=openapi.TYPE_OBJECT, description="Пользовательские данные по площадкам в формате {site_id: {descriptions: [{title, author, abundance, ...}, ...], metadata: {site_number, zone_type}}, ...}"),
            },
            required=['elements', 'custom_data'],
        ),
        responses={
            200: openapi.Response(description="Результаты анализа пользовательских данных", schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'data': openapi.Schema(type=openapi.TYPE_OBJECT)})),
            400: "Неверные параметры",
            401: "Не авторизован",
        },
    )
    def post(self, request):
        elements = request.data.get('elements', [])
        custom_data = request.data.get('custom_data', {})
        if not elements:
            return self.prepare_error_response("Необходимо указать хотя бы один элемент для сравнения")
        if not custom_data:
            return self.prepare_error_response("Необходимо предоставить данные для анализа")

        valid_elements = SUPPORTED_SPECTRUM_TYPES + list(SCALES_DICT.keys())
        invalid_elements = [elem for elem in elements if elem not in valid_elements]
        if invalid_elements:
            return self.prepare_error_response(f"Неверные элементы: {', '.join(invalid_elements)}. Доступные элементы: {', '.join(valid_elements)}")

        for site_id, site_data in custom_data.items():
            if not isinstance(site_data, dict):
                return self.prepare_error_response(f"Неверный формат данных для площадки {site_id}. Должен быть словарь с ключами 'descriptions' и 'metadata'.")
            descriptions = site_data.get('descriptions', [])
            if not isinstance(descriptions, list):
                return self.prepare_error_response(f"Неверный формат описаний для площадки {site_id}. Должен быть список описаний.")

        analysis_results = analyze_custom_data(custom_data, elements)
        if not analysis_results:
            return self.prepare_error_response("Не удалось провести анализ данных")

        return Response({'data': analysis_results}, status=status.HTTP_200_OK)




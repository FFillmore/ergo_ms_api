from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.modules.bio.ml.model_loader import clear_cache


class ModelCacheView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Управление кешем моделей машинного обучения",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['clear'], description="Действие с кешем"),
            },
            required=['action'],
        ),
        responses={
            200: openapi.Response(
                description="Результат операции",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}),
            ),
            400: 'Неверное действие',
            401: "Не авторизован",
        },
    )
    def post(self, request):
        action = request.data.get('action')
        if action == 'clear':
            clear_cache()
            return Response({'message': 'Кеш моделей очищен успешно'})
        return Response({'error': 'Неизвестное действие. Доступные действия: clear'}, status=400)




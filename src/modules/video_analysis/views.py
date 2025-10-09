import logging
import os
from pathlib import Path

from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework import viewsets, status
from django.apps import apps
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin
from src.modules.video_analysis.models import VideoAnalysis
from src.modules.video_analysis.serializers import (
    VideoAnalysisSerializer, 
    BulkVideoAnalysisCreateSerializer,
    VideoAnalysisCreateSerializer,
    VideoAnalysisUpdateSerializer
)
from src.modules.video_analysis.tasks import translate_video_analysis

# Получаем логгер для модуля
logger = logging.getLogger('video_analysis')

class VideoAnalysisViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """
    Только просмотр анализов текущего пользователя (list/retrieve)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VideoAnalysisSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'status']
    ordering = ['-created_at']
    
    # Пагинация: поддержка ?page и ?page_size
    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 5
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        base_queryset = VideoAnalysis.objects.all()
        user = self.get_safe_user()
        if user:
            logger.debug(f"Получение queryset для пользователя {user.username} (ID: {user.id})")
            return self.get_safe_queryset(base_queryset.filter(user=user))
        return self.get_safe_queryset(base_queryset.none())
    
    def list(self, request, *args, **kwargs):
        logger.info(f"Запрос списка анализов от пользователя {request.user.username} (ID: {request.user.id})")
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        analysis_id = kwargs.get('pk')
        logger.info(f"Запрос анализа {analysis_id} от пользователя {request.user.username} (ID: {request.user.id})")
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Обновить название и описание анализа.
        """
        analysis = self.get_object()
        serializer = VideoAnalysisUpdateSerializer(analysis, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Логируем изменения
        old_title = analysis.title
        old_description = analysis.description
        new_title = serializer.validated_data.get('title', old_title)
        new_description = serializer.validated_data.get('description', old_description)
        
        logger.info(f"Обновление анализа {analysis.id} от пользователя {request.user.username}: "
                   f"название '{old_title}' -> '{new_title}', "
                   f"описание '{old_description}' -> '{new_description}'")
        
        serializer.save()
        
        return Response({
            'detail': 'Анализ успешно обновлен',
            'analysis': VideoAnalysisSerializer(analysis).data
        }, status=status.HTTP_200_OK) 

    def create(self, request, *args, **kwargs):
        """
        Создать анализ: загрузить видео и запустить задачу перевода.
        Формат: multipart/form-data с полем 'video' и опционально 'title'.
        """
        serializer = VideoAnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_safe_user()
        uploaded_file = serializer.validated_data['video']
        title = serializer.validated_data.get('title', '')
        
        # Получаем настройки субтитров
        subtitle_lines_count = serializer.validated_data.get('subtitle_lines_count', 1)
        subtitle_font_size = serializer.validated_data.get('subtitle_font_size', 24)
        subtitle_font_color = serializer.validated_data.get('subtitle_font_color', '#FFFFFF')
        subtitle_background_color = serializer.validated_data.get('subtitle_background_color', '#000000')
        subtitle_background_transparent = serializer.validated_data.get('subtitle_background_transparent', True)
        subtitle_alignment = serializer.validated_data.get('subtitle_alignment', 'bottom')
        subtitle_margin_vertical = serializer.validated_data.get('subtitle_margin_vertical', 20)
        subtitle_margin_horizontal = serializer.validated_data.get('subtitle_margin_horizontal', 0)
        
        # Преобразуем строковые boolean значения для create метода
        if isinstance(subtitle_background_transparent, str):
            subtitle_background_transparent = subtitle_background_transparent.lower() in ('true', '1', 'yes', 'on')
        elif subtitle_background_transparent is None:
            subtitle_background_transparent = True
        
        # Получаем настройки TTS
        tts_enabled = serializer.validated_data.get('tts_enabled', False)
        tts_volume = serializer.validated_data.get('tts_volume', 0.7)
        tts_language = serializer.validated_data.get('tts_language', 'fr')
        tts_voice_model = serializer.validated_data.get('tts_voice_model', 'silero_tts')
        
        # Если название не задано, используем "Автоматический анализ"
        if not title:
            title = 'Автоматический анализ'

        # Создаем анализ в БД для получения UUID
        analysis = VideoAnalysis.objects.create(
            user=user,
            title=title,
            description='Автоматический анализ видео',
            status='pending',
            subtitle_lines_count=subtitle_lines_count,
            subtitle_font_size=subtitle_font_size,
            subtitle_font_color=subtitle_font_color,
            subtitle_background_color=subtitle_background_color,
            subtitle_background_transparent=subtitle_background_transparent,
            subtitle_alignment=subtitle_alignment,
            subtitle_margin_vertical=subtitle_margin_vertical,
            subtitle_margin_horizontal=subtitle_margin_horizontal,
            tts_enabled=tts_enabled,
            tts_volume=tts_volume,
            tts_language=tts_language,
            tts_voice_model=tts_voice_model
        )

        # Получаем расширение файла
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        # Формируем имя файла как UUID + расширение
        uuid_filename = f"{analysis.id}{file_extension}"

        # Сохраняем исходное видео с именем UUID
        from src.modules.video_analysis.apps import VideoAnalysisConfig
        initial_dir = Path(VideoAnalysisConfig.INITIAL_VIDEO_DIR)
        initial_dir.mkdir(parents=True, exist_ok=True)

        target_path = initial_dir / uuid_filename
        with open(target_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Обновляем путь к файлу в анализе
        analysis.original_video = f'video_analysis/initial_video/{uuid_filename}'
        analysis.save()

        # Запускаем задачу обработки с UUID файла
        # Берем настройку использования GPU из конфигурации приложения
        use_gpu_default = getattr(apps.get_app_config('video_analysis'), 'USE_GPU', None)
        async_result = translate_video_analysis.delay(
            uuid_filename, 
            user_id=user.id, 
            title=title, 
            use_gpu=use_gpu_default,
            analysis_uuid=str(analysis.id)
        )
        
        # Сохраняем task_id
        analysis.task_id = async_result.id
        analysis.save()

        return Response({
            'detail': 'Задача обработки видео запущена',
            'task_id': async_result.id,
            'analysis_id': str(analysis.id),
            'file': uuid_filename,
            'title': title
        }, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        analysis: VideoAnalysis = self.get_object()
        try:
            # Принудительная очистка всех файлов по UUID
            analysis.force_cleanup_all_files()
            logger.info(f"Все файлы анализа {analysis.id} успешно удалены")
        except Exception as e:
            logger.error(f"Ошибка при удалении файлов анализа {analysis.id}: {e}")
            # Продолжаем удаление записи из БД даже если файлы не удалились
        
        response = super().destroy(request, *args, **kwargs)
        return response

    @action(detail=True, methods=['get'], url_path='download_file')
    def download_file(self, request, pk=None):
        """
        Скачать один из файлов результатов. Параметр query 'type' либо 'path'.
        type: audio|subtitles|video
        path: относительный путь внутри MEDIA_ROOT (приоритетнее)
        """
        # Логируем информацию о запросе для отладки
        logger.info(f"Запрос скачивания файла от пользователя {request.user.username} (ID: {request.user.id})")
        logger.info(f"Заголовки запроса: {dict(request.headers)}")
        logger.info(f"Параметры запроса: {request.query_params}")
        
        analysis: VideoAnalysis = self.get_object()
        rel_path = request.query_params.get('path')
        file_type = request.query_params.get('type')

        def build_abs(rel):
            from src.modules.video_analysis.apps import VideoAnalysisConfig
            abs_path = Path(VideoAnalysisConfig.MEDIA_ROOT) / rel
            return abs_path

        abs_path = None
        if rel_path:
            abs_path = build_abs(rel_path)
        elif file_type == 'audio' and analysis.audio_file:
            abs_path = build_abs(analysis.audio_file)
        elif file_type == 'subtitles' and analysis.subtitles_file:
            abs_path = build_abs(analysis.subtitles_file)
        elif file_type == 'video' and analysis.output_video:
            abs_path = build_abs(analysis.output_video)
        elif file_type == 'tts_audio' and analysis.tts_audio_file:
            abs_path = build_abs(analysis.tts_audio_file)

        if not abs_path or not abs_path.exists():
            raise Http404('Файл не найден')

        file_handle = open(abs_path, 'rb')
        response = FileResponse(file_handle)
        response["Content-Disposition"] = f"attachment; filename={abs_path.name}"
        return response

    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        """
        Создать несколько анализов одновременно.
        Формат: multipart/form-data с полями 'videos[]' и опционально 'titles[]'.
        """
        # Преобразуем данные в формат для сериализатора
        videos = request.FILES.getlist('videos')
        titles = request.data.getlist('titles', [])
        
        # Получаем настройки субтитров
        subtitle_lines_count = int(request.data.get('subtitle_lines_count', 1))
        subtitle_font_size = int(request.data.get('subtitle_font_size', 24))
        subtitle_font_color = request.data.get('subtitle_font_color', '#FFFFFF')
        subtitle_background_color = request.data.get('subtitle_background_color', '#000000')
        subtitle_background_transparent = request.data.get('subtitle_background_transparent', True)
        subtitle_alignment = request.data.get('subtitle_alignment', 'bottom')
        subtitle_margin_vertical = int(request.data.get('subtitle_margin_vertical', 20))
        subtitle_margin_horizontal = int(request.data.get('subtitle_margin_horizontal', 0))
        
        # Получаем настройки TTS
        tts_enabled = request.data.get('tts_enabled', False)
        tts_volume = float(request.data.get('tts_volume', 0.7))
        tts_language = request.data.get('tts_language', 'fr')
        tts_voice_model = request.data.get('tts_voice_model', 'silero_tts')
        
        # Преобразуем строковые boolean значения
        if isinstance(subtitle_background_transparent, str):
            subtitle_background_transparent = subtitle_background_transparent.lower() in ('true', '1', 'yes', 'on')
        elif subtitle_background_transparent is None:
            subtitle_background_transparent = True
        
        if isinstance(tts_enabled, str):
            tts_enabled = tts_enabled.lower() in ('true', '1', 'yes', 'on')
        elif tts_enabled is None:
            tts_enabled = False
        
        logger.info(f"Получены настройки субтитров: lines={subtitle_lines_count}, size={subtitle_font_size}, "
                   f"font_color={subtitle_font_color}, bg_color={subtitle_background_color}, "
                   f"transparent={subtitle_background_transparent}")
        logger.info(f"Все данные запроса: {dict(request.data)}")
        
        if not videos:
            return Response({
                'detail': 'Необходимо загрузить хотя бы один видео файл'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Валидируем данные
        serializer = BulkVideoAnalysisCreateSerializer(data={
            'videos': videos,
            'titles': titles if titles else [],
            'subtitle_lines_count': subtitle_lines_count,
            'subtitle_font_size': subtitle_font_size,
            'subtitle_font_color': subtitle_font_color,
            'subtitle_background_color': subtitle_background_color,
            'subtitle_background_transparent': subtitle_background_transparent,
            'subtitle_alignment': subtitle_alignment,
            'subtitle_margin_vertical': subtitle_margin_vertical,
            'subtitle_margin_horizontal': subtitle_margin_horizontal,
            'tts_enabled': tts_enabled,
            'tts_volume': tts_volume,
            'tts_language': tts_language,
            'tts_voice_model': tts_voice_model
        })
        serializer.is_valid(raise_exception=True)
        
        user = self.get_safe_user()
        validated_data = serializer.validated_data
        videos = validated_data['videos']
        titles = validated_data.get('titles', [])
        
        # Получаем настройки субтитров
        subtitle_lines_count = validated_data.get('subtitle_lines_count', 1)
        subtitle_font_size = validated_data.get('subtitle_font_size', 24)
        subtitle_font_color = validated_data.get('subtitle_font_color', '#FFFFFF')
        subtitle_background_color = validated_data.get('subtitle_background_color', '#000000')
        subtitle_background_transparent = validated_data.get('subtitle_background_transparent', True)
        subtitle_alignment = validated_data.get('subtitle_alignment', 'bottom')
        subtitle_margin_vertical = validated_data.get('subtitle_margin_vertical', 20)
        subtitle_margin_horizontal = validated_data.get('subtitle_margin_horizontal', 0)
        
        # Получаем настройки TTS
        tts_enabled = validated_data.get('tts_enabled', False)
        tts_volume = validated_data.get('tts_volume', 0.7)
        tts_language = validated_data.get('tts_language', 'fr')
        tts_voice_model = validated_data.get('tts_voice_model', 'silero_tts')
        
        # Создаем папку для загрузки
        from src.modules.video_analysis.apps import VideoAnalysisConfig
        initial_dir = Path(VideoAnalysisConfig.INITIAL_VIDEO_DIR)
        initial_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for i, uploaded_file in enumerate(videos):
            try:
                # Определяем название
                title = titles[i] if i < len(titles) and titles[i] else ''
                if not title:
                    title = 'Автоматический анализ'
                
                # Создаем анализ в БД для получения UUID
                analysis = VideoAnalysis.objects.create(
                    user=user,
                    title=title,
                    description='Автоматический анализ видео',
                    status='pending',
                    subtitle_lines_count=subtitle_lines_count,
                    subtitle_font_size=subtitle_font_size,
                    subtitle_font_color=subtitle_font_color,
                    subtitle_background_color=subtitle_background_color,
                    subtitle_background_transparent=subtitle_background_transparent,
                    subtitle_alignment=subtitle_alignment,
                    subtitle_margin_vertical=subtitle_margin_vertical,
                    subtitle_margin_horizontal=subtitle_margin_horizontal,
                    tts_enabled=tts_enabled,
                    tts_volume=tts_volume,
                    tts_language=tts_language,
                    tts_voice_model=tts_voice_model
                )

                # Получаем расширение файла
                file_extension = os.path.splitext(uploaded_file.name)[1]
                
                # Формируем имя файла как UUID + расширение
                uuid_filename = f"{analysis.id}{file_extension}"
                
                # Сохраняем файл с UUID именем
                target_path = initial_dir / uuid_filename
                
                with open(target_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Обновляем путь к файлу в анализе
                analysis.original_video = f'video_analysis/initial_video/{uuid_filename}'
                analysis.save()
                
                # Запускаем задачу обработки с UUID файла
                # Берем настройку использования GPU из конфигурации приложения
                use_gpu_default = getattr(apps.get_app_config('video_analysis'), 'USE_GPU', None)
                async_result = translate_video_analysis.delay(
                    uuid_filename, 
                    user_id=user.id, 
                    title=title,
                    use_gpu=use_gpu_default,
                    analysis_uuid=str(analysis.id)
                )
                
                # Сохраняем task_id
                analysis.task_id = async_result.id
                analysis.save()
                
                results.append({
                    'file': uuid_filename,
                    'original_name': uploaded_file.name,
                    'title': title,
                    'analysis_id': str(analysis.id),
                    'task_id': async_result.id,
                    'status': 'started'
                })
                
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {uploaded_file.name}: {str(e)}")
                results.append({
                    'file': uploaded_file.name,
                    'title': titles[i] if i < len(titles) else '',
                    'status': 'error',
                    'error': str(e)
                })
        
        return Response({
            'detail': f'Запущена обработка {len([r for r in results if r["status"] == "started"])} видео',
            'results': results
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['post'], url_path='bulk_delete')
    def bulk_delete(self, request):
        """
        Массовое удаление анализов текущего пользователя.
        Ожидает JSON: { ids: [uuid, ...] }
        """
        user = self.get_safe_user()
        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return Response({'detail': 'Передайте список идентификаторов в поле ids'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_safe_queryset(VideoAnalysis.objects.filter(user=user, id__in=ids))
        to_delete = list(queryset)

        deleted, errors = 0, []
        for analysis in to_delete:
            try:
                analysis.force_cleanup_all_files()
                analysis.delete()
                deleted += 1
            except Exception as e:
                logger.error(f"Ошибка при массовом удалении анализа {analysis.id}: {e}")
                errors.append({'id': str(analysis.id), 'error': str(e)})

        return Response({
            'detail': f'Удалено {deleted} анализов',
            'deleted': deleted,
            'errors': errors
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Статистика по анализам текущего пользователя.
        """
        queryset = self.get_queryset()
        total = queryset.count()
        by_status = {
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='completed').count(),
            'failed': queryset.filter(status='failed').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
        }
        total_segments = sum((q.subtitle_count or 0) for q in queryset)
        total_duration = sum((q.duration or 0) for q in queryset)
        return Response({
            'total': total,
            'by_status': by_status,
            'total_segments': total_segments,
            'total_duration': total_duration,
        })

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_analysis(self, request, pk=None):
        """
        Отменить выполнение анализа
        """
        analysis = self.get_object()
        
        # Проверяем, что анализ можно отменить
        if analysis.status not in ['pending', 'processing']:
            return Response({
                'detail': f'Нельзя отменить анализ со статусом "{analysis.status}"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Отменяем задачу Celery, если она есть
            if analysis.task_id:
                from celery import current_app
                current_app.control.revoke(analysis.task_id, terminate=True)
                logger.info(f"Задача Celery {analysis.task_id} отменена для анализа {analysis.id}")
            
            # Обновляем статус анализа
            analysis.update_status('cancelled', error_message='Анализ отменен пользователем')
            
            logger.info(f"Анализ {analysis.id} отменен пользователем {request.user.username}")
            
            return Response({
                'detail': 'Анализ успешно отменен',
                'analysis': VideoAnalysisSerializer(analysis).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при отмене анализа {analysis.id}: {e}")
            return Response({
                'detail': 'Ошибка при отмене анализа',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='cleanup-orphaned-files')
    def cleanup_orphaned_files(self, request):
        """
        Очищает осиротевшие файлы - файлы без привязки к анализам.
        Требует права администратора.
        """
        user = self.get_safe_user()
        
        # Проверяем права (можно настроить по необходимости)
        if not user.is_staff:
            return Response({
                'detail': 'Недостаточно прав для выполнения операции'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            deleted_count = VideoAnalysis.cleanup_orphaned_files()
            
            return Response({
                'detail': f'Очистка осиротевших файлов завершена',
                'deleted_count': deleted_count,
                'message': f'Удалено {deleted_count} осиротевших файлов'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при очистке осиротевших файлов: {e}")
            return Response({
                'detail': 'Ошибка при очистке осиротевших файлов',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
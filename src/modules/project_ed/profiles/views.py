from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404

from src.core.utils.mixins import SwaggerSafeMixin
from .models import UserProfile
from .serializers import (
    UserDetailSerializer, 
    UserListSerializer, 
    UserProfileSerializer
)

User = get_user_model()


class UserProfileViewSet(SwaggerSafeMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра профилей пользователей."""
    
    queryset = User.objects.select_related(
        'project_ed_profile__role_ref',
        'project_ed_profile__position_ref', 
        'project_ed_profile__faculty_ref',
        'project_ed_profile__department_ref',
        'avatar'
    ).all()
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserDetailSerializer
    
    def _is_project_ed_admin(self, user):
        profile = getattr(user, 'project_ed_profile', None)
        try:
            role_name = getattr(profile, 'role_name', None)
        except Exception:
            role_name = None
        return bool(role_name == 'Администратор') or bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))

    def get_queryset(self):
        """Фильтрация пользователей."""
        queryset = super().get_queryset()
        
        # Фильтрация по поиску
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Фильтрация по должности
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(
                project_ed_profile__position_ref__name__icontains=position
            )
        position_exact = self.request.query_params.get('position_exact')
        if position_exact:
            queryset = queryset.filter(
                project_ed_profile__position_ref__name__iexact=position_exact
            )

        # Фильтрация по роли
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(
                project_ed_profile__role_ref__name__icontains=role
            )
        role_exact = self.request.query_params.get('role_exact')
        if role_exact:
            queryset = queryset.filter(
                project_ed_profile__role_ref__name__iexact=role_exact
            )
        
        # Фильтрация по факультету
        faculty = self.request.query_params.get('faculty')
        if faculty:
            queryset = queryset.filter(
                project_ed_profile__faculty_ref__name__icontains=faculty
            )
        
        # Фильтрация по кафедре
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(
                project_ed_profile__department_ref__name__icontains=department
            )
        
        # Только публичные профили для обычных пользователей; админам — все
        if not self._is_project_ed_admin(self.request.user):
            include_private = str(self.request.query_params.get('include_private', '')).lower() in ('1', 'true', 'yes')
            # Если явно просили приватные, но не админ — игнорируем флаг
            # Разрешаем автоматически видеть руководителей (ректор/проректор), чтобы наполнялись селекты
            position_query = (self.request.query_params.get('position') or '').lower()
            position_exact_query = (self.request.query_params.get('position_exact') or '').lower()
            is_leadership_query = ('ректор' in position_query) or ('проректор' in position_query) or ('ректор' in position_exact_query) or ('проректор' in position_exact_query)
            if not include_private and not is_leadership_query:
                queryset = queryset.filter(
                    models.Q(project_ed_profile__isnull=True) |  # Если нет профиля, считаем публичным
                    models.Q(project_ed_profile__is_public=True)
                )
        
        return queryset.order_by('first_name', 'last_name')

    @action(detail=False, methods=['get'])
    def leadership(self, request):
        """
        Список пользователей по руководящим должностям.
        Поддерживаем параметры:
        - position: подстрочный поиск (например, 'ректор' или 'проректор')
        - position_exact: точное совпадение названия должности

        Для этого эндпоинта ослабляем фильтр приватности, чтобы упростить наполнение селектов.
        """
        position = (request.query_params.get('position') or '').strip()
        position_exact = (request.query_params.get('position_exact') or '').strip()

        qs = super().get_queryset()
        if position_exact:
            qs = qs.filter(project_ed_profile__position_ref__name__iexact=position_exact)
        elif position:
            qs = qs.filter(project_ed_profile__position_ref__name__icontains=position)
        else:
            # По умолчанию возвращаем всех, у кого позиция содержит 'ректор'
            qs = qs.filter(project_ed_profile__position_ref__name__icontains='ректор')

        # Этот спец-эндпоинт намеренно не режет приватность, чтобы заполнить выпадающие списки
        serializer = UserListSerializer(qs.order_by('first_name', 'last_name'), many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Получить проекты пользователя."""
        user = self.get_object()
        projects = user.project_ed_projects.all()
        
        # Сериализуем проекты (можно создать отдельный сериализатор)
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'short_name': project.short_name,
                'status': project.status,
                'start_date': project.start_date,
                'end_date': project.end_date,
                'created_at': project.created_at,
            })
        
        return Response(projects_data)
    


class UserProfileSettingsViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для управления настройками профиля пользователя."""
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def _is_project_ed_admin(self, user):
        """Проверка: является ли пользователь администратором ProjectEd по роли профиля."""
        profile = getattr(user, 'project_ed_profile', None)
        try:
            role_name = getattr(profile, 'role_name', None)
        except Exception:
            role_name = None
        return bool(role_name == 'Администратор') or bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))
    
    def get_queryset(self):
        """ProjectEd-админы видят все профили, остальные — только свой."""
        # Для генерации Swagger схемы
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return self.queryset.none()
        
        if self._is_project_ed_admin(user):
            return self.queryset
        return self.queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """Upsert-поведение с поддержкой ProjectEd-админа: можно указать иного пользователя."""
        request_user = self.request.user
        target_user = serializer.validated_data.get('user') if self._is_project_ed_admin(request_user) else request_user
        if target_user is None:
            target_user = request_user

        profile, _ = UserProfile.objects.get_or_create(user=target_user, defaults={'user': target_user})
        for field in ['role_ref', 'position_ref', 'faculty_ref', 'department_ref', 'is_public', 'show_email']:
            if field in serializer.validated_data:
                setattr(profile, field, serializer.validated_data[field])
        profile.save()
        serializer.instance = profile
    
    def get_object(self):
        """ProjectEd-админ получает по pk; обычный пользователь — свой профиль."""
        user = self.request.user
        if self._is_project_ed_admin(user):
            return super().get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'user': user})
        return profile


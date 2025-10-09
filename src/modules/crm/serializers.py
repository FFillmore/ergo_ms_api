from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Project, ProjectMember, Task, TaskComment, TaskAttachment, TimeLog,
    ProjectStatus, ProjectPriority, TaskStatus, TaskPriority
)

User = get_user_model()


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов проектов"""
    
    class Meta:
        model = ProjectStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов проектов"""
    
    class Meta:
        model = ProjectPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов задач"""
    
    class Meta:
        model = TaskStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов задач"""
    
    class Meta:
        model = TaskPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CRMUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'avatar_url']

    def get_avatar_url(self, obj):
        # Ожидаем связь one-to-one: user.avatar.image
        avatar = getattr(obj, 'avatar', None)
        image = getattr(avatar, 'image', None)
        if image and hasattr(image, 'url'):
            request = self.context.get('request')
            try:
                url = image.url
                return request.build_absolute_uri(url) if request else url
            except Exception:
                # На случай, если storage не может отдать url
                return None
        return None


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника проекта"""
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""
    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    memberships = ProjectMemberSerializer(many=True, read_only=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'manager_id',
            'memberships', 'status', 'priority', 'start_date', 'end_date',
            'created_at', 'updated_at', 'color', 'task_count', 'completed_task_count',
            'progress', 'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]
        ref_name = 'CRMProject'
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q
        
        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)
        
        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')
        
        return obj.tasks.filter(new_system_filter | old_system_filter).count()
    
    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0
        
        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Сериализатор списка проектов"""
    owner = CRMUserSerializer(read_only=True)
    manager = CRMUserSerializer(read_only=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = ProjectStatusSerializer(read_only=True)
    priority_ref = ProjectPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'owner', 'manager', 'status', 'priority',
            'start_date', 'end_date', 'created_at', 'color', 'task_count',
            'completed_task_count', 'progress', 'status_ref', 'priority_ref',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        """Получить количество завершенных задач (учитываем новую и старую систему статусов)"""
        from django.db.models import Q
        
        # Фильтр для новой системы статусов (status_ref.is_final = True)
        new_system_filter = Q(status_ref__is_final=True, status_ref__is_active=True)
        
        # Фильтр для старой системы статусов (status = 'done')
        old_system_filter = Q(status='done')
        
        return obj.tasks.filter(new_system_filter | old_system_filter).count()
    
    def get_progress(self, obj):
        """Вычислить прогресс проекта в процентах"""
        total = obj.tasks.count()
        if total == 0:
            return 0
        
        completed = self.get_completed_task_count(obj)
        return round((completed / total) * 100)


class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к задаче"""
    author = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор прикрепленного файла"""
    uploaded_by = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'uploaded_by', 'uploaded_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class TimeLogSerializer(serializers.ModelSerializer):
    """Сериализатор учета времени"""
    user = CRMUserSerializer(read_only=True)
    
    class Meta:
        model = TimeLog
        fields = ['id', 'description', 'hours', 'date', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""
    assignee = CRMUserSerializer(read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_id = serializers.IntegerField(write_only=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    status_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    priority_ref_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Дополнительные поля
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    # Поля дат с дополнительной обработкой
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    time_logs = TimeLogSerializer(many=True, read_only=True)
    total_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_id', 'assignee', 'assignee_id',
            'creator', 'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours', 'kanban_order',
            'comments', 'attachments', 'time_logs', 'total_time',
            'status_ref', 'priority_ref', 'status_ref_id', 'priority_ref_id',
            'current_status', 'current_priority', 'status_display', 'priority_display'
        ]
    
    def get_total_time(self, obj):
        return sum(log.hours for log in obj.time_logs.all())
    
    def validate(self, data):
        """Дополнительная валидация данных задачи"""
        # Проверяем что дата окончания не раньше даты начала
        if data.get('start_date') and data.get('due_date'):
            if data['due_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "Дата окончания не может быть раньше даты начала"
                )
        
        return data
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Сериализатор списка задач"""
    assignee = CRMUserSerializer(read_only=True)
    creator = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    
    # Новые поля для статусов и приоритетов
    status_ref = TaskStatusSerializer(read_only=True)
    priority_ref = TaskPrioritySerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    current_priority = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    priority_display = serializers.CharField(read_only=True)
    
    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'creator',
            'status', 'priority', 'start_date', 'due_date', 'completed_at',
            'created_at', 'updated_at', 'estimated_hours', 'actual_hours',
            'kanban_order', 'comment_count', 'attachment_count',
            'status_ref', 'priority_ref', 'current_status', 'current_priority',
            'status_display', 'priority_display'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()


class TaskCalendarSerializer(serializers.ModelSerializer):
    """Сериализатор задач для календаря"""
    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'start_date', 'due_date', 'created_at'
        ]


class TaskKanbanSerializer(serializers.ModelSerializer):
    """Сериализатор задач для канбан доски"""
    assignee = CRMUserSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'assignee', 'status',
            'priority', 'due_date', 'kanban_order', 'estimated_hours'
        ]
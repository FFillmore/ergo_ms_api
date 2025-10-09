from rest_framework import serializers
import json
from decimal import Decimal, ROUND_HALF_UP

from src.modules.project_ed.models import (
    Project, Category, Subcategory, TargetIndicator, EventBlock, Event,
    Role, Position, Faculty, Department
)


class ProjectSerializer(serializers.ModelSerializer):
    # Принимаем гибкие входы
    budget_total = serializers.FloatField(required=False)
    additional_info = serializers.JSONField(required=False, allow_null=True)
    class Meta:
        model = Project
        fields = [
            'id',
            'owner',
            'status',
            'event_block_id',
            'event_id',
            'short_name',
            'name',
            'name_clarification',
            'goal',
            'start_date',
            'end_date',
            'curator_id',
            'customer_id',
            'manager_id',
            'budget_total',
            'additional_info',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']
        ref_name = 'ProjectEdProject'

    def validate_budget_total(self, value):
        try:
            return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            return value

    def validate_additional_info(self, value):
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
        return str(value)

    def create(self, validated_data):
        # Нормализуем значения перед сохранением
        bt = validated_data.pop('budget_total', None)
        ai = validated_data.pop('additional_info', None)

        if bt is not None:
            try:
                validated_data['budget_total'] = Decimal(str(bt)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except Exception:
                validated_data['budget_total'] = Decimal('0.00')

        if ai is not None:
            if isinstance(ai, (dict, list)):
                try:
                    validated_data['additional_info'] = json.dumps(ai, ensure_ascii=False)
                except Exception:
                    validated_data['additional_info'] = str(ai)
            else:
                validated_data['additional_info'] = str(ai)

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        bt = validated_data.pop('budget_total', None)
        ai = validated_data.pop('additional_info', None)

        if bt is not None:
            try:
                validated_data['budget_total'] = Decimal(str(bt)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except Exception:
                pass

        if ai is not None:
            if isinstance(ai, (dict, list)):
                try:
                    validated_data['additional_info'] = json.dumps(ai, ensure_ascii=False)
                except Exception:
                    validated_data['additional_info'] = str(ai)
            else:
                validated_data['additional_info'] = str(ai)

        return super().update(instance, validated_data)

    def validate(self, attrs):
        start = attrs.get('start_date') or getattr(self.instance, 'start_date', None)
        end = attrs.get('end_date') or getattr(self.instance, 'end_date', None)
        if start and end and start >= end:
            raise serializers.ValidationError('Дата начала должна быть раньше даты окончания')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор для подкатегорий."""
    indicators_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Subcategory
        fields = [
            'id',
            'name',
            'description',
            'order',
            'is_active',
            'indicators_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['indicators_count', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    subcategories = SubcategorySerializer(many=True, read_only=True)
    indicators_count = serializers.ReadOnlyField()
    subcategories_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'order',
            'is_active',
            'indicators_count',
            'subcategories_count',
            'subcategories',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['indicators_count', 'subcategories_count', 'created_at', 'updated_at']
        ref_name = 'ProjectEdCategory'


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления категорий с подкатегориями."""
    subcategories = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'order',
            'is_active',
            'subcategories',
        ]
    
    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category.objects.create(**validated_data)
        
        # Создаем подкатегории
        for index, subcategory_name in enumerate(subcategories_data):
            if subcategory_name.strip():  # Пропускаем пустые названия
                Subcategory.objects.create(
                    category=category,
                    name=subcategory_name.strip(),
                    order=index
                )
        
        return category
    
    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)
        
        # Обновляем основную информацию категории
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем подкатегории, если они переданы
        if subcategories_data is not None:
            # Удаляем существующие подкатегории
            instance.subcategories.all().delete()
            
            # Создаем новые подкатегории
            for index, subcategory_name in enumerate(subcategories_data):
                if subcategory_name.strip():  # Пропускаем пустые названия
                    Subcategory.objects.create(
                        category=instance,
                        name=subcategory_name.strip(),
                        order=index
                    )
        
        return instance


class TargetIndicatorSerializer(serializers.ModelSerializer):
    """Сериализатор для целевых показателей."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_description = serializers.CharField(source='category.description', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    event_block_title = serializers.CharField(source='event_block.title', read_only=True)
    event_block_short_name = serializers.SerializerMethodField()
    responsible_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TargetIndicator
        fields = [
            'id',
            'category',
            'subcategory',
            'category_name',
            'category_description',
            'subcategory_name',
            'name',
            'unit',
            'event_block',
            'event_block_title',
            'event_block_short_name',
            'responsible',
            'responsible_name',
            'values_by_year',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_responsible_name(self, obj):
        """Получить полное имя ответственного."""
        if obj.responsible:
            return f"{obj.responsible.first_name} {obj.responsible.last_name}".strip() or obj.responsible.username
        return None

    def get_event_block_short_name(self, obj):
        blk = getattr(obj, 'event_block', None)
        if not blk:
            return None
        # Короткое имя: предпочитаем код, иначе заголовок
        return getattr(blk, 'code', None) or getattr(blk, 'title', None)
    
    # Убрана валидация привязки подкатегории к категории


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор для мероприятий."""
    years_display = serializers.ReadOnlyField()
    unique_leaders_count = serializers.ReadOnlyField()
    leaders = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id',
            'block',
            'code',
            'name',
            'results',
            'start_year',
            'end_year',
            'years_display',
            'unique_leaders_count',
            'leaders',
            'order',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['years_display', 'unique_leaders_count', 'leaders', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Валидация: год начала не может быть больше года окончания."""
        start_year = attrs.get('start_year')
        end_year = attrs.get('end_year')
        
        if start_year and end_year and start_year > end_year:
            raise serializers.ValidationError(
                'Год начала не может быть больше года окончания.'
            )
        
        return attrs


class EventBlockSerializer(serializers.ModelSerializer):
    """Сериализатор для блоков мероприятий."""
    events = EventSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='subcategory.category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    events_count = serializers.ReadOnlyField()
    
    class Meta:
        model = EventBlock
        fields = [
            'id',
            'code',
            'title',
            'description',
            'subcategory',
            'category_name',
            'subcategory_name',
            'events',
            'events_count',
            'order',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['category_name', 'subcategory_name', 'events_count', 'created_at', 'updated_at']
    
    # Убрана валидация привязки подкатегории к категории


class EventBlockCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления блоков мероприятий с мероприятиями."""
    events = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    category_name = serializers.CharField(source='subcategory.category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    events_count = serializers.ReadOnlyField()
    
    class Meta:
        model = EventBlock
        fields = [
            'id',
            'code',
            'title',
            'description',
            'subcategory',
            'category_name',
            'subcategory_name',
            'events',
            'events_count',
            'order',
            'is_active',
        ]
    
    # Убрана валидация привязки подкатегории к категории
    
    def create(self, validated_data):
        events_data = validated_data.pop('events', [])
        event_block = EventBlock.objects.create(**validated_data)
        
        # Создаем мероприятия
        for index, event_data in enumerate(events_data):
            if event_data.get('name', '').strip():  # Пропускаем пустые названия
                Event.objects.create(
                    block=event_block,
                    order=index,
                    **event_data
                )
        
        return event_block
    
    def update(self, instance, validated_data):
        events_data = validated_data.pop('events', None)
        
        # Обновляем основную информацию блока
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем мероприятия, если они переданы
        if events_data is not None:
            # Удаляем существующие мероприятия
            instance.events.all().delete()
            
            # Создаем новые мероприятия
            for index, event_data in enumerate(events_data):
                if event_data.get('name', '').strip():  # Пропускаем пустые названия
                    Event.objects.create(
                        block=instance,
                        order=index,
                        **event_data
                    )
        
        return instance


class ProjectEdRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
        read_only_fields = []


class ProjectEdPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']
        read_only_fields = []


class ProjectEdFacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'short_name']
        read_only_fields = []


class ProjectEdDepartmentSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all(), required=False, allow_null=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    faculty_short_name = serializers.CharField(source='faculty.short_name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'short_name', 'faculty', 'faculty_name', 'faculty_short_name']
        read_only_fields = ['faculty_name', 'faculty_short_name']
import os

from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from .models import UploadedFile
from .models import Category
from .models import Tag
from .models import UserAvatar
from .models import (
    GeneralSettings, AppearanceSettings,
    SecuritySettings, MediaSettings, PermalinkSettings, EmailSettings, AuditLog
)

class UploadedFileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    dl_url = serializers.SerializerMethodField()

    class Meta:
        model  = UploadedFile
        fields = ['id', 'file', 'name', 'size',
                  'alt_name', 'url', 'dl_url', 'uploaded_at']

    def get_name(self, obj):
        return os.path.basename(obj.file.name)

    def get_size(self, obj):
        return obj.file.size

    def get_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.file.url) if req else obj.file.url

    def get_dl_url(self, obj):
        req = self.context.get('request')
        filename = obj.alt_name or os.path.basename(obj.file.name)
        rel = f"settings/files/{filename}"
        return req.build_absolute_uri(f"/api/{rel}") if req else f"/api/{rel}"
    
class GeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = '__all__'

class AppearanceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppearanceSettings
        fields = '__all__'

class SecuritySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecuritySettings
        fields = '__all__'

class MediaSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaSettings
        fields = '__all__'

class PermalinkSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermalinkSettings
        fields = '__all__'

class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSettings
        fields = '__all__'
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'slug']
        read_only_fields = ['slug']
        ref_name = 'SettingsCategory'
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['slug'] = instance.slug
        return ret
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'category']
class UserAvatarSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = UserAvatar
        fields = ['id', 'user', 'image', 'uploaded_at']

class AuditLogSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field='model'
    )
    user = serializers.CharField(
        source='user.username',
        default=None,
        read_only=True
    )
    action = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'content_type',
            'object_id',
            'action',
            'changes',
            'user',
            'timestamp',
        ]
        read_only_fields = fields

    def get_action(self, obj):
        return obj.get_action_display()
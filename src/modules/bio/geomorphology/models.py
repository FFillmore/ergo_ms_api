from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Site


class SoilProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    profile_id = models.CharField(max_length=100, verbose_name='Идентификатор профиля')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Долгота')
    depth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Глубина разреза (см)')
    collection_date = models.DateField(null=True, blank=True, verbose_name='Дата отбора')
    soil_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип почвы')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'bio_geomorphology_profiles'
        verbose_name = 'Почвенный профиль'
        verbose_name_plural = 'Почвенные профили'
        constraints = [
            models.UniqueConstraint(fields=['user', 'profile_id'], name='unique_user_profile_id'),
        ]
        indexes = [
            models.Index(fields=['user', 'profile_id']),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}"


class SoilLayer(models.Model):
    profile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, related_name='layers', verbose_name='Профиль')
    depth_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Глубина от (см)')
    depth_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Глубина до (см)')
    color = models.CharField(max_length=50, null=True, blank=True, verbose_name='Цвет')
    texture = models.CharField(max_length=100, null=True, blank=True, verbose_name='Текстура')
    structure = models.CharField(max_length=100, null=True, blank=True, verbose_name='Структура')
    moisture = models.CharField(max_length=50, null=True, blank=True, verbose_name='Влажность')
    ph_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='pH')
    organic_matter = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Орг. вещество (%)')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'bio_geomorphology_layers'
        verbose_name = 'Почвенный слой'
        verbose_name_plural = 'Почвенные слои'
        indexes = [
            models.Index(fields=['profile']),
        ]

    def __str__(self) -> str:
        return f"Layer {self.depth_from}-{self.depth_to} cm"


class SoilProfileImage(models.Model):
    profile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, related_name='images', verbose_name='Профиль')
    file = models.FileField(upload_to='bio/geomorphology/', verbose_name='Файл')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'bio_geomorphology_images'
        verbose_name = 'Изображение почвенного профиля'
        verbose_name_plural = 'Изображения почвенных профилей'

    def __str__(self) -> str:
        return f"Image for {self.profile}"



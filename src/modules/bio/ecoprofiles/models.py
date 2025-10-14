from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Site


class EcologicalProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=255, verbose_name='Название профиля')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'bio_ecoprofiles_profiles'
        verbose_name = 'Экологический профиль'
        verbose_name_plural = 'Экологические профили'

    def __str__(self) -> str:
        return f"{self.name}"


class ProfileSite(models.Model):
    profile = models.ForeignKey(EcologicalProfile, on_delete=models.CASCADE, related_name='profile_sites', verbose_name='Профиль')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    distance_from_start = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Расстояние от начала (м)')
    elevation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Высота (м)')

    class Meta:
        db_table = 'bio_ecoprofiles_profile_sites'
        verbose_name = 'Площадка профиля'
        verbose_name_plural = 'Площадки профиля'
        constraints = [
            models.UniqueConstraint(fields=['profile', 'site'], name='unique_profile_site'),
        ]
        indexes = [
            models.Index(fields=['profile']),
            models.Index(fields=['site']),
        ]

    def __str__(self) -> str:
        return f"{self.profile} - {self.site}"




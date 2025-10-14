from django.db import models
from django.contrib.auth.models import User


class PollenSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    sample_id = models.CharField(max_length=100, verbose_name='Идентификатор образца')
    collection_date = models.DateField(null=True, blank=True, verbose_name='Дата отбора')
    depth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Глубина')
    age = models.IntegerField(null=True, blank=True, verbose_name='Возраст')
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Долгота')

    class Meta:
        db_table = 'bio_paleobotany_samples'
        verbose_name = 'Образец пыльцы'
        verbose_name_plural = 'Образцы пыльцы'
        indexes = [
            models.Index(fields=['user', 'sample_id']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'sample_id'], name='unique_user_sample_id'),
        ]

    def __str__(self) -> str:
        return f"{self.sample_id}"


class PollenImage(models.Model):
    sample = models.ForeignKey(PollenSample, on_delete=models.CASCADE, related_name='images', verbose_name='Образец')
    file = models.FileField(upload_to='bio/paleobotany/', verbose_name='Файл')
    magnification = models.CharField(max_length=50, null=True, blank=True, verbose_name='Увеличение')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'bio_paleobotany_images'
        verbose_name = 'Изображение образца пыльцы'
        verbose_name_plural = 'Изображения образцов пыльцы'

    def __str__(self) -> str:
        return f"Image for {self.sample}"



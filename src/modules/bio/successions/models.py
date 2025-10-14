from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Site, Species


class Succession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    name = models.CharField(max_length=255, verbose_name='Название')
    succession_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип сукцессии')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')

    class Meta:
        db_table = 'bio_successions'
        verbose_name = 'Сукцессия'
        verbose_name_plural = 'Сукцессии'

    def __str__(self) -> str:
        return f"{self.name}"


class SuccessionStage(models.Model):
    succession = models.ForeignKey(Succession, on_delete=models.CASCADE, related_name='stages', verbose_name='Сукцессия')
    stage_number = models.PositiveIntegerField(verbose_name='Номер стадии')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата завершения')
    duration_years = models.PositiveIntegerField(null=True, blank=True, verbose_name='Длительность (годы)')

    class Meta:
        db_table = 'bio_succession_stages'
        verbose_name = 'Стадия сукцессии'
        verbose_name_plural = 'Стадии сукцессии'
        constraints = [
            models.UniqueConstraint(fields=['succession', 'stage_number'], name='unique_succession_stage_number'),
        ]

    def __str__(self) -> str:
        return f"{self.succession} - stage {self.stage_number}"


class SuccessionSpecies(models.Model):
    ABUNDANCE_CHOICES = [('r', 'Единично'), ('+', 'До 1%'), ('1', 'До 5%'), ('2', '5-25%'), ('3', '25-50%'), ('4', '50-75%'), ('5', '75-100%')]

    stage = models.ForeignKey(SuccessionStage, on_delete=models.CASCADE, related_name='stage_species', verbose_name='Стадия')
    plant_species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name='Вид растения')
    abundance = models.CharField(max_length=3, choices=ABUNDANCE_CHOICES, null=True, blank=True, verbose_name='Обилие')
    notes = models.TextField(null=True, blank=True, verbose_name='Примечания')

    class Meta:
        db_table = 'bio_succession_species'
        verbose_name = 'Вид на стадии сукцессии'
        verbose_name_plural = 'Виды на стадиях сукцессии'
        constraints = [
            models.UniqueConstraint(fields=['stage', 'plant_species'], name='unique_stage_plant_species'),
        ]

    def __str__(self) -> str:
        return f"{self.plant_species} @ {self.stage}"



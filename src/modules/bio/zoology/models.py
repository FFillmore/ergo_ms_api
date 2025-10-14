from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Site, Species  # прямой импорт для избежания циклов


class AnimalSpecies(models.Model):
    species_id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название вида')
    author = models.CharField(max_length=255, verbose_name='Автор вида')
    latin_name = models.CharField(max_length=255, verbose_name='Латинское название', db_index=True)

    taxon_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип таксона')
    conservation_status = models.CharField(max_length=100, null=True, blank=True, verbose_name='Охранный статус')
    habitat_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип местообитания')
    diet_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип питания')
    life_span = models.CharField(max_length=100, null=True, blank=True, verbose_name='Продолжительность жизни')
    migration_pattern = models.CharField(max_length=255, null=True, blank=True, verbose_name='Миграции')

    tax_class = models.CharField(max_length=100, null=True, blank=True, verbose_name='Класс')
    tax_order = models.CharField(max_length=100, null=True, blank=True, verbose_name='Отряд')
    tax_family = models.CharField(max_length=100, null=True, blank=True, verbose_name='Семейство')
    animal_type = models.CharField(max_length=32, null=True, blank=True, verbose_name='Тип животного (vertebrate/invertebrate)')

    class Meta:
        db_table = 'bio_zoology_species'
        verbose_name = 'Вид животного'
        verbose_name_plural = 'Виды животных'
        constraints = [
            models.UniqueConstraint(fields=['latin_name', 'author'], name='unique_animal_latin_author'),
        ]

    def __str__(self) -> str:
        return f"{self.latin_name} ({self.author})"


class AnimalPopulation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    animal_species = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE, verbose_name='Вид животного')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    observation_date = models.DateField(null=True, blank=True, verbose_name='Дата наблюдения')

    estimated_count = models.IntegerField(null=True, blank=True, verbose_name='Оценка численности')
    density = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='Плотность')
    age_structure = models.JSONField(null=True, blank=True, verbose_name='Возрастная структура')
    notes = models.TextField(null=True, blank=True, verbose_name='Примечания')

    class Meta:
        db_table = 'bio_zoology_populations'
        verbose_name = 'Популяция животных'
        verbose_name_plural = 'Популяции животных'
        indexes = [
            models.Index(fields=['user', 'site']),
            models.Index(fields=['animal_species']),
        ]

    def __str__(self) -> str:
        return f"{self.animal_species} @ {self.site}"


class AnimalObservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    animal_species = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE, verbose_name='Вид животного')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    population = models.ForeignKey(AnimalPopulation, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Связанная популяция')

    observation_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время наблюдения')
    gender = models.CharField(max_length=32, null=True, blank=True, verbose_name='Пол')
    age = models.CharField(max_length=32, null=True, blank=True, verbose_name='Возраст')
    behavior = models.TextField(null=True, blank=True, verbose_name='Поведение')
    notes = models.TextField(null=True, blank=True, verbose_name='Примечания')

    class Meta:
        db_table = 'bio_zoology_observations'
        verbose_name = 'Наблюдение животного'
        verbose_name_plural = 'Наблюдения животных'
        indexes = [
            models.Index(fields=['user', 'site']),
            models.Index(fields=['animal_species']),
        ]

    def __str__(self) -> str:
        return f"{self.animal_species} observed @ {self.site}"



from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Species, Site
from src.modules.bio.zoology.models import AnimalSpecies


class SpeciesInteraction(models.Model):
    INTERACTION_CHOICES = [
        ('predation', 'predation'),
        ('pollination', 'pollination'),
        ('seed_dispersal', 'seed_dispersal'),
        ('parasitism', 'parasitism'),
        ('commensalism', 'commensalism'),
        ('mutualism', 'mutualism'),
        ('competition', 'competition'),
        ('habitat', 'habitat'),
        ('food', 'food'),
        ('other', 'other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    plant_species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name='Вид растения')
    animal_species = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE, verbose_name='Вид животного')
    interaction_type = models.CharField(max_length=32, choices=INTERACTION_CHOICES, verbose_name='Тип взаимодействия')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    observed_date = models.DateField(null=True, blank=True, verbose_name='Дата наблюдения')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Площадка')

    class Meta:
        db_table = 'bio_interactions_records'
        verbose_name = 'Взаимодействие видов'
        verbose_name_plural = 'Взаимодействия видов'
        indexes = [
            models.Index(fields=['user', 'site']),
            models.Index(fields=['plant_species']),
            models.Index(fields=['animal_species']),
        ]

    def __str__(self) -> str:
        return f"{self.plant_species} x {self.animal_species} ({self.interaction_type})"



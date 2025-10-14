from django.db import models
from django.contrib.auth.models import User

from src.modules.bio.geobotany.models import Species


class FloristicList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        db_table = 'bio_floristics_lists'
        verbose_name = 'Флористический список'
        verbose_name_plural = 'Флористические списки'

    def __str__(self) -> str:
        return f"{self.name}"


class FloristicListItem(models.Model):
    ABUNDANCE_CHOICES = [('r', 'Единично'), ('+', 'До 1%'), ('1', 'До 5%'), ('2', '5-25%'), ('3', '25-50%'), ('4', '50-75%'), ('5', '75-100%')]

    list = models.ForeignKey(FloristicList, on_delete=models.CASCADE, related_name='items', verbose_name='Список')
    species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name='Вид растения')
    abundance = models.CharField(max_length=3, choices=ABUNDANCE_CHOICES, null=True, blank=True, verbose_name='Обилие')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    class Meta:
        db_table = 'bio_floristics_items'
        verbose_name = 'Элемент флористического списка'
        verbose_name_plural = 'Элементы флористического списка'
        constraints = [
            models.UniqueConstraint(fields=['list', 'species'], name='unique_list_species'),
        ]

    def __str__(self) -> str:
        return f"{self.species} in {self.list}"



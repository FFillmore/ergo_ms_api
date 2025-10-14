from django.db import models
from django.contrib.auth.models import User


class Species(models.Model):
    species_id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Название вида')
    author = models.CharField(max_length=255, verbose_name='Автор вида')

    # Landolt
    lLight = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала относительной освещенности (Landolt)')
    lTemperature = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала теплолюбивости (Landolt)')
    lContinentality = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала континентальности (Landolt)')
    lMoisture = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала влажности (Landolt)')
    lReaction = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала кислотности почвы (Landolt)')
    lNutrient = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала обеспеченности почвы минеральным азотом (Landolt)')
    lHumus = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала гумуса (Landolt)')
    lDispersion = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала дисперсии (Landolt)')

    # Ellenberg
    eLight = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала относительной освещенности (Ellenberg)')
    eTemperature = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала теплолюбивости (Ellenberg)')
    eContinentality = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала континентальности (Ellenberg)')
    eMoisture = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала влажности (Ellenberg)')
    eReaction = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала кислотности почвы (Ellenberg)')
    eNutrient = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала обеспеченности почвы минеральным азотом (Ellenberg)')

    # Tsyganov
    tm1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала термоклиматическая минимум (Цыганов)')
    tm2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала термоклиматическая максимум (Цыганов)')
    kn1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала континентальности климата минимум (Цыганов)')
    kn2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала континентальности климата максимум (Цыганов)')
    om1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала влажности климата минимум (Цыганов)')
    om2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала влажности климата максимум (Цыганов)')
    cr1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала морозности климата минимум (Цыганов)')
    cr2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала морозности климата максимум (Цыганов)')
    hd1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала увлажнения почвы минимум (Цыганов)')
    hd2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала увлажнения почвы максимум (Цыганов)')
    tr1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала солевого режима почвы минимум (Цыганов)')
    tr2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала солевого режима почвы максимум (Цыганов)')
    nt1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала обеспеченности почвы минеральным азотом минимум (Цыганов)')
    nt2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала обеспеченности почвы минеральным азотом максимум (Цыганов)')
    rc1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала кислотности почвы минимум (Цыганов)')
    rc2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала кислотности почвы максимум (Цыганов)')
    lc1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала освещенности минимум (Цыганов)')
    lc2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала освещенности максимум (Цыганов)')
    fh1 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала переменности увлажнения минимум (Цыганов)')
    fh2 = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Шкала переменности увлажнения максимум (Цыганов)')

    # Biological traits
    raunkiaer = models.CharField(max_length=10, null=True, blank=True, verbose_name='Жизненная форма по Раункиеру')
    serebryakov = models.CharField(max_length=10, null=True, blank=True, verbose_name='Жизненная форма по Серебрякову')
    ecobiomorphs = models.CharField(max_length=10, null=True, blank=True, verbose_name='Экобиоморфа')
    geoelements = models.CharField(max_length=10, null=True, blank=True, verbose_name='Геоэлемент')
    ta = models.CharField(max_length=10, null=True, blank=True, verbose_name='Тип ареала')

    class Meta:
        db_table = "bio_species"
        verbose_name = "Вид растения"
        verbose_name_plural = "Виды растений"
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author')
        ]

    def __str__(self):
        return f"{self.title} ({self.author})"


class Site(models.Model):
    ZONE_TYPE_CHOICES = [('forest', 'Лес'), ('meadow', 'Луг')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    site_number = models.IntegerField(verbose_name='Номер площадки')
    zone_type = models.CharField(max_length=10, choices=ZONE_TYPE_CHOICES, verbose_name='Тип местности')
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Размер площадки (м²)')
    date = models.DateField(null=True, blank=True, verbose_name='Дата создания площадки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')

    # geo
    latitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name='Долгота')
    district = models.CharField(max_length=100, null=True, blank=True, verbose_name='Район')
    mapped_point = models.CharField(max_length=100, null=True, blank=True, verbose_name='Привязка к карте')
    mapped_point_distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Расстояние от точки привязки (м)')
    mapped_point_azimuth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Азимут от точки привязки (°)')
    forestry_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Название лесничества')

    # relief
    center_distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Расстояние от центра (м)')
    center_azimuth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Азимут от центра (°)')
    mesorelief_shape = models.CharField(max_length=100, null=True, blank=True, verbose_name='Форма мезорельефа')
    exposition = models.CharField(max_length=100, null=True, blank=True, verbose_name='Экспозиция склона')
    steepness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Крутизна склона (°)')
    position_relief = models.CharField(max_length=100, null=True, blank=True, verbose_name='Положение в рельефе')
    microrelief_shape = models.CharField(max_length=100, null=True, blank=True, verbose_name='Форма микрорельефа')

    # moisture/soil
    humidification_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='Тип увлажнения')
    groundwater_level = models.CharField(max_length=100, null=True, blank=True, verbose_name='Уровень грунтовых вод')

    # deadwood/litter
    brushwood_compos = models.CharField(max_length=100, null=True, blank=True, verbose_name='Состав валежника')
    brushwood_diameter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Диаметр валежника (см)')
    brushwood_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Количество валежника')
    decomposition_degree = models.CharField(max_length=100, null=True, blank=True, verbose_name='Степень разложения подстилки')

    class Meta:
        db_table = "bio_sites"
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"
        constraints = [
            models.UniqueConstraint(fields=['user', 'site_number', 'zone_type'], name='unique_user_site_zone')
        ]
        indexes = [models.Index(fields=['user', 'site_number', 'zone_type'])]

    def __str__(self):
        return f"{self.site_number} ({self.zone_type}) - {self.user.username}"


class Description(models.Model):
    TIER_CHOICES = [('', 'Нет'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')]
    ABUNDANCE_CHOICES = [('r', 'Единично'), ('+', 'До 1%'), ('1', 'До 5%'), ('2', '5-25%'), ('3', '25-50%'), ('4', '50-75%'), ('5', '75-100%')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    species = models.ForeignKey(Species, on_delete=models.CASCADE, verbose_name='Вид')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Площадка')
    tier = models.CharField(max_length=3, choices=TIER_CHOICES, blank=True, verbose_name='Ярус')
    abundance = models.CharField(max_length=3, choices=ABUNDANCE_CHOICES, verbose_name='Обилие')

    class Meta:
        db_table = "bio_descriptions"
        verbose_name = "Описание вида"
        verbose_name_plural = "Описания видов"
        constraints = [
            models.UniqueConstraint(fields=['user', 'species', 'site', 'tier'], name='unique_description')
        ]
        indexes = [models.Index(fields=['user', 'species', 'site'])]

    def __str__(self):
        return f"{self.species} на площадке {self.site.site_number} в ярусе {self.tier or 'без яруса'} (обилие: {self.abundance})"




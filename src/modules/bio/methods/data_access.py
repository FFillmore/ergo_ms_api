import pandas as pd
from django.shortcuts import get_object_or_404

from src.modules.bio.models import Species, Site, Description
from src.modules.bio.constants import (
    ABUNDANCE_SYMBOLS_TO_VALUES,
    SCALES_DICT,
    SUPPORTED_SPECTRUM_TYPES,
)


def get_species_data_from_site(user, site_number, zone_type):
    """
    Возвращает DataFrame с данными о видах и их обилии на площадке по её номеру и типу местности.
    """
    site = get_object_or_404(Site, user=user, site_number=site_number, zone_type=zone_type)

    descriptions = (
        Description.objects
        .filter(site=site)
        .select_related('species')
        .values(
            'abundance',
            'species__species_id',
            'species__title',
            'species__author',
            'species__raunkiaer',
            'species__serebryakov',
            'species__ecobiomorphs',
            'species__geoelements',
            'species__ta',
            'species__eLight',
            'species__eTemperature',
            'species__eContinentality',
            'species__eMoisture',
            'species__eReaction',
            'species__eNutrient',
            'species__lLight',
            'species__lTemperature',
            'species__lContinentality',
            'species__lMoisture',
            'species__lReaction',
            'species__lNutrient',
            'species__lHumus',
            'species__lDispersion',
            'species__tm1', 'species__tm2',
            'species__kn1', 'species__kn2',
            'species__om1', 'species__om2',
            'species__cr1', 'species__cr2',
            'species__hd1', 'species__hd2',
            'species__tr1', 'species__tr2',
            'species__nt1', 'species__nt2',
            'species__rc1', 'species__rc2',
            'species__lc1', 'species__lc2',
            'species__fh1', 'species__fh2',
        )
    )

    data = list(descriptions)

    for item in data:
        abundance_symbol = item.get('abundance', '')
        item['abundance_numeric'] = ABUNDANCE_SYMBOLS_TO_VALUES.get(abundance_symbol, 0)
        for key in list(item.keys()):
            if key.startswith('species__'):
                item[key[9:]] = item.pop(key)

    df = pd.DataFrame(data)
    return df


def get_unique_values(column):
    """
    Получает уникальные значения для указанного столбца модели Species,
    исключая '0', null и пустые строки.
    """
    return (
        Species.objects
        .exclude(**{column: '0'})
        .exclude(**{column: ''})
        .exclude(**{column: None})
        .values_list(column, flat=True)
        .distinct()
        .order_by(column)
    )


def get_species_data_by_site_id(user, site_id):
    """
    Возвращает DataFrame с данными о видах и их обилии на площадке по её ID.
    """
    try:
        site = Site.objects.get(id=site_id, user=user)
    except Site.DoesNotExist:
        return None

    descriptions = (
        Description.objects
        .filter(site=site)
        .select_related('species')
        .values(
            'abundance',
            'species__species_id',
            'species__title',
            'species__author',
            'species__raunkiaer',
            'species__serebryakov',
            'species__ecobiomorphs',
            'species__geoelements',
            'species__ta',
            'species__eLight',
            'species__eTemperature',
            'species__eContinentality',
            'species__eMoisture',
            'species__eReaction',
            'species__eNutrient',
            'species__lLight',
            'species__lTemperature',
            'species__lContinentality',
            'species__lMoisture',
            'species__lReaction',
            'species__lNutrient',
            'species__lHumus',
            'species__lDispersion',
            'species__tm1', 'species__tm2',
            'species__kn1', 'species__kn2',
            'species__om1', 'species__om2',
            'species__cr1', 'species__cr2',
            'species__hd1', 'species__hd2',
            'species__tr1', 'species__tr2',
            'species__nt1', 'species__nt2',
            'species__rc1', 'species__rc2',
            'species__lc1', 'species__lc2',
            'species__fh1', 'species__fh2',
        )
    )

    data = list(descriptions)

    for item in data:
        abundance_symbol = item.get('abundance', '')
        item['abundance_numeric'] = ABUNDANCE_SYMBOLS_TO_VALUES.get(abundance_symbol, 0)
        for key in list(item.keys()):
            if key.startswith('species__'):
                item[key[9:]] = item.pop(key)

    df = pd.DataFrame(data)
    return df


def get_species_data_by_custom_data(descriptions, scale_type=None):
    """
    Извлекает данные о растениях из пользовательских данных.

    Args:
        descriptions: список описаний видов с полями title, author, abundance
        scale_type: тип шкалы для извлечения данных (опционально)

    Returns:
        DataFrame с данными о видах или None, если данные не найдены
    """
    all_species = set()
    for desc in descriptions:
        if 'title' in desc and 'author' in desc:
            all_species.add((desc['title'], desc['author']))

    if not all_species:
        return None

    species_map = {}
    titles, authors = zip(*all_species)
    db_species = Species.objects.filter(title__in=titles, author__in=authors)

    for species in db_species:
        species_map[(species.title, species.author)] = species

    site_data_records = []

    for desc in descriptions:
        if 'title' not in desc or 'author' not in desc or 'abundance' not in desc:
            continue

        species_key = (desc['title'], desc['author'])
        if species_key not in species_map:
            continue

        species = species_map[species_key]

        record = {
            'title': species.title,
            'author': species.author,
            'abundance': desc['abundance'],
            'abundance_numeric': ABUNDANCE_SYMBOLS_TO_VALUES.get(desc['abundance'], 0)
        }

        if scale_type and scale_type in SCALES_DICT:
            for scale_field, _ in SCALES_DICT[scale_type]:
                if hasattr(species, scale_field):
                    record[scale_field] = getattr(species, scale_field)
        else:
            for spectrum in SUPPORTED_SPECTRUM_TYPES:
                if hasattr(species, spectrum):
                    record[spectrum] = getattr(species, spectrum)

            for scale_type_key in SCALES_DICT:
                for field, _ in SCALES_DICT[scale_type_key]:
                    if hasattr(species, field):
                        record[field] = getattr(species, field)

        site_data_records.append(record)

    if not site_data_records:
        return None

    return pd.DataFrame(site_data_records)




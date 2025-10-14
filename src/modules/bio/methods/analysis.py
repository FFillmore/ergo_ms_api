import pandas as pd

from src.modules.bio.models import Species, Site
from src.modules.bio.constants import SCALES_DICT, SUPPORTED_SPECTRUM_TYPES
from .data_access import get_unique_values, get_species_data_by_site_id


def calculate_means(data: pd.DataFrame, scale_type: str) -> pd.DataFrame | None:
    if scale_type not in SCALES_DICT:
        return None

    scale_fields = [field for field, _ in SCALES_DICT[scale_type]]
    display_names = [display for _, display in SCALES_DICT[scale_type]]

    df = data[scale_fields].fillna(0).replace('', 0)

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df = df[(df != 0).any(axis=1)]
    if df.empty:
        return pd.DataFrame({'scale': display_names, 'value': [0] * len(display_names)})

    means = df.mean()
    result_df = pd.DataFrame({'scale': display_names, 'value': means.values})
    return result_df


def calculate_spectrums_percentage_distribution(data: pd.DataFrame, spectrum_type: str) -> pd.DataFrame | None:
    if spectrum_type not in data.columns:
        return None

    data_spectrum = data[spectrum_type]
    data_spectrum = data_spectrum[(data_spectrum != '0') & (data_spectrum != '') & (data_spectrum.notna())]

    elements = sorted(get_unique_values(spectrum_type))
    if data_spectrum.empty:
        return pd.DataFrame({'scale': elements, 'value': [0] * len(elements)})

    elements_counts = data_spectrum.value_counts()
    for el in elements:
        if el not in elements_counts:
            elements_counts[el] = 0

    elements_counts = elements_counts.reindex(elements).fillna(0)
    total_species_with_elements = elements_counts.sum()
    if total_species_with_elements == 0:
        return pd.DataFrame({'scale': elements, 'value': [0] * len(elements)})

    percentage_distribution = (elements_counts / total_species_with_elements) * 100
    distribution_df = pd.DataFrame({
        'scale': elements_counts.index,
        'value': percentage_distribution.values
    })
    return distribution_df


def calculate_scales_percentage_distribution(data: pd.DataFrame, scale_type: str) -> pd.DataFrame | None:
    if scale_type not in SCALES_DICT:
        return None

    scale_fields = [field for field, _ in SCALES_DICT[scale_type]]
    display_names = [display for _, display in SCALES_DICT[scale_type]]

    df = data[scale_fields].fillna(0).replace('', 0)
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    sums = df.sum()
    total_sum = sums.sum()
    if total_sum == 0:
        return pd.DataFrame({'scale': display_names, 'value': [0] * len(display_names)})

    percentage_distribution = (sums / total_sum) * 100
    result_df = pd.DataFrame({'scale': display_names, 'value': percentage_distribution.values})
    return result_df


def get_comparison_data(user, site_ids: list[int], comparison_elements: list[str]) -> dict:
    result: dict = {}
    spectra_types = SUPPORTED_SPECTRUM_TYPES
    scale_types = [scale_type for scale_type in comparison_elements if scale_type in SCALES_DICT]

    for site_id in site_ids:
        try:
            try:
                site = Site.objects.get(id=site_id, user=user)
                site_info = {
                    'id': site.id,
                    'site_number': site.site_number,
                    'zone_type': site.zone_type,
                }
            except Site.DoesNotExist:
                continue

            site_data = get_species_data_by_site_id(user, site_id)
            if site_data is None or site_data.empty:
                continue

            site_key = f"site_{site_id}"
            result[site_key] = {
                'info': site_info,
                'data': {}
            }

            for spectrum_type in comparison_elements:
                if spectrum_type in spectra_types:
                    distribution = calculate_spectrums_percentage_distribution(site_data, spectrum_type)
                    if distribution is not None:
                        result[site_key]['data'][spectrum_type] = distribution.to_dict(orient='records')

            for scale_type in scale_types:
                distribution = calculate_scales_percentage_distribution(site_data, scale_type)
                if distribution is not None:
                    result[site_key]['data'][scale_type] = distribution.to_dict(orient='records')

        except Exception:
            continue

    return result


def analyze_custom_data(custom_data: dict, comparison_elements: list[str]) -> dict:
    result: dict = {}
    spectra_types = SUPPORTED_SPECTRUM_TYPES
    scale_types = [scale_type for scale_type in comparison_elements if scale_type in SCALES_DICT]

    all_species: set[tuple[str, str]] = set()
    for _, site_data in custom_data.items():
        descriptions = site_data.get('descriptions', [])
        for desc in descriptions:
            if 'title' in desc and 'author' in desc:
                all_species.add((desc['title'], desc['author']))

    species_map: dict[tuple[str, str], Species] = {}
    if all_species:
        titles, authors = zip(*all_species)
        db_species = Species.objects.filter(title__in=titles, author__in=authors)
        for species in db_species:
            species_map[(species.title, species.author)] = species

    for site_id, site_data in custom_data.items():
        descriptions = site_data.get('descriptions', [])
        metadata = site_data.get('metadata', {})

        site_data_records: list[dict] = []
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
                'abundance_numeric': (
                    # lightweight import to avoid circular
                    __import__('src.modules.bio.constants', fromlist=['ABUNDANCE_SYMBOLS_TO_VALUES']).ABUNDANCE_SYMBOLS_TO_VALUES.get(desc['abundance'], 0)  # type: ignore
                ),
            }

            for spectrum in spectra_types:
                if hasattr(species, spectrum):
                    record[spectrum] = getattr(species, spectrum)

            for scale_type in scale_types:
                for field, _ in SCALES_DICT[scale_type]:
                    if hasattr(species, field):
                        record[field] = getattr(species, field)

            site_data_records.append(record)

        if not site_data_records:
            continue

        site_df = pd.DataFrame(site_data_records)

        site_info = {
            'id': site_id,
            'site_number': metadata.get('site_number', ''),
            'zone_type': metadata.get('zone_type', ''),
        }

        site_key = f"site_{site_id}"
        result[site_key] = {
            'info': site_info,
            'data': {}
        }

        for spectrum_type in comparison_elements:
            if spectrum_type in spectra_types:
                distribution = calculate_spectrums_percentage_distribution(site_df, spectrum_type)
                if distribution is not None:
                    result[site_key]['data'][spectrum_type] = distribution.to_dict(orient='records')

        for scale_type in scale_types:
            distribution = calculate_scales_percentage_distribution(site_df, scale_type)
            if distribution is not None:
                result[site_key]['data'][scale_type] = distribution.to_dict(orient='records')

    return result




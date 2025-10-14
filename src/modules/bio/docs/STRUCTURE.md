# Bio module structure

## Directory layout

- `src/modules/bio/constants.py`: shared constants (`SCALES_DICT`, `SUPPORTED_SPECTRUM_TYPES`, etc.)
- `src/modules/bio/urls.py`: app-level routes aggregation
- `src/modules/bio/ml/`: ML utilities (e.g., `model_loader`)
- `src/modules/bio/methods/` (service layer)
  - `data_access.py`: site/species data extraction helpers
  - `analysis.py`: calculations (means, spectra/scales distributions, comparison)
  - `__init__.py`: public function exports (`from src.modules.bio.methods import ...`)
- `src/modules/bio/views/` (API layer - shared)
  - `base.py`: pagination (`StandardResultsSetPagination`)
  - `maintenance.py`: model cache management endpoint
  - `__init__.py`: exports only shared items

## Domains (submodules)

Each domain lives under `src/modules/bio/<domain>/` with a standard structure:
- `models.py`: domain-specific models
- `serializers.py`: domain serializers
- `views/`: domain endpoints (split per concern if needed)
- `urls.py`: domain routes (mounted under `/api/bio/<domain>/`)

Implemented domains:
- `geobotany/` — plant `Species`, `Site`, `Description`; base helpers and analytics live under `geobotany/views/` (split by concern)
- `zoology/` — `AnimalSpecies`, `AnimalPopulation`, `AnimalObservation`
- `ecoprofiles/` — `EcologicalProfile`, `ProfileSite`
- `interactions/` — `SpeciesInteraction`
- `successions/` — `Succession`, `SuccessionStage`, `SuccessionSpecies`
- `paleobotany/` — `PollenSample`, `PollenImage`
- `geomorphology/` — `SoilProfile`, `SoilLayer`, `SoilProfileImage`
- `floristics/` — `FloristicList`, `FloristicListItem`

Root re-exports:
- `src/modules/bio/models.py` → re-exports all domain models
- `src/modules/bio/serializers.py` → re-exports all domain serializers
- `src/modules/bio/docs/STRUCTURE.md`: this guide

## Public entry points

- Views (endpoints):
  - Prefer HTTP usage via URLs. If importing, import domain views from `src.modules.bio.<domain>.views.*`.
  - Shared views (base/maintenance) live in `src.modules.bio.views`.
- Methods (services):
  - Import service functions from `src.modules.bio.methods`
  - Example: `from src.modules.bio.methods import calculate_means`
- Models/serializers:
  - Import via root modules: `from src.modules.bio.models import ...` or `from src.modules.bio.serializers import ...`

## Endpoints and URLs

- App-level `src/modules/bio/urls.py` aggregates domain routes via `include(...)` under prefixes:
  - `geobotany/`, `zoology/`, `ecoprofiles/`, `interactions/`, `successions/`, `paleobotany/`, `geomorphology/`, `floristics/`
- Shared maintenance endpoint is exposed at: `models/cache/`

## Adding a new endpoint

1. Choose a domain file in `views/` (or create a new one) and implement the view/class.
2. Reuse helpers from `views/base.py` for validation and standard responses.
3. Register the route in the domain `urls.py` and include it from `src/modules/bio/urls.py`.
4. Add/adjust serializers in the appropriate domain.

## Adding a new data/analysis operation

1. Implement data fetching in `methods/data_access.py` or calculations in `methods/analysis.py`.
2. Export the function in `methods/__init__.py`.
3. Call the function from the corresponding view in `views/`.

## Common helpers and conventions

- Use `BaseDescriptionView` and `BaseSiteAnalyticsView` (in `views/base.py`) for:
  - `zone_type` validation
  - standardized error/not-found responses
  - fetching site data where applicable
- Prefer type hints in service functions.
- Keep `urls.py` the single source of truth for routing.
- Place ML-related code in `ml/`; use `model_loader.get_model(zone_type)` from views that perform classification.

## Adding new domain

To add a new domain under `src/modules/bio/<domain>/`:

- Create `models.py`, `serializers.py`, optional `methods/`, `views/`, and `urls.py`.
- Aggregate models in the app-level `models.py` (via re-exports), and routes in `src/modules/bio/urls.py` under a domain prefix:
```python
urlpatterns += [
  path('zoology/', include('src.modules.bio.zoology.urls')),
  path('ecoprofiles/', include('src.modules.bio.ecoprofiles.urls')),
  # ...
]
```

### Split policy

- Root `models.py` and `serializers.py` are thin re-exports; keep all domain-specific code in domain packages.
- Thresholds for further splitting within a domain:
  - File approaches ~400–500 lines or contains >~8–10 classes/functions with different concerns.
  - The domain introduces distinct sub-areas; then split into subpackages inside the domain.

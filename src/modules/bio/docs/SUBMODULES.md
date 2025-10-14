## BIO submodules overview

This document briefly describes implemented submodules, their purpose, core models, and basic CRUD scope. Analytics is intentionally out of scope.

### Geobotany (`src/modules/bio/geobotany/`)
- Purpose: core vegetation data (plant species, sites, descriptions) and shared analytics endpoints used by other modules.
- Models:
  - `Species` (global reference): plant species with ecological scales and spectra traits.
  - `Site` (user-scoped): geobotanical sites with location and habitat metadata.
  - `Description` (user-scoped): species tier and abundance on a site.
- Endpoints (prefix `/api/bio/geobotany/`):
  - `species/`, `sites/`, descriptions: `sites/<site_number>/<zone_type>/descriptions/`
  - analytics: `means/`, `distribution/`, `classification/`, `comparison/`, `custom-*` routes under `sites/...`

View split guideline: where appropriate, split `views/` into `base.py`, `analytics.py`, and feature-focused files to keep modules maintainable. Apply similar splitting in other domains when they grow.

### Zoology (`src/modules/bio/zoology/`)
- Purpose: record animal species reference data, populations and observations on sites.
- Models:
  - `AnimalSpecies` (global reference): latin/vernacular name, author, basic taxonomy and traits.
  - `AnimalPopulation` (user-scoped): species at `Site` with counts, density, age structure.
  - `AnimalObservation` (user-scoped): point observations with optional link to a population.
- CRUD: `species/`, `populations/`, `observations/` (standard list/retrieve/create/update/delete).

### Ecoprofiles (`src/modules/bio/ecoprofiles/`)
- Purpose: build ecological profiles with linked sites and distances/elevations.
- Models:
  - `EcologicalProfile` (user-scoped): name, description, created date.
  - `ProfileSite` (child): link profile to `Site` with `distance_from_start`, `elevation`.
- CRUD: `profiles/`, `profile-sites/`.

### Interactions (`src/modules/bio/interactions/`)
- Purpose: register plant–animal interactions (pollination, predation, etc.).
- Models:
  - `SpeciesInteraction` (user-scoped): plant `Species`, animal `AnimalSpecies`, type, optional `Site`.
- CRUD: `interactions/`.

### Successions (`src/modules/bio/successions/`)
- Purpose: record succession processes by stages and species composition.
- Models:
  - `Succession` (user-scoped): basic meta and linked `Site`.
  - `SuccessionStage` (child): sequential stages (unique stage_number per succession).
  - `SuccessionSpecies` (child): plant `Species` abundance per stage.
- CRUD: `successions/`, `stages/`, `stage-species/`.

### Paleobotany (`src/modules/bio/paleobotany/`)
- Purpose: store pollen samples and related images.
- Models:
  - `PollenSample` (user-scoped): sample id, depth/age, coordinates.
  - `PollenImage` (child): file, magnification, description.
- CRUD: `samples/`, `images/`.

### Geomorphology (`src/modules/bio/geomorphology/`)
- Purpose: store soil profiles, layers and images.
- Models:
  - `SoilProfile` (user-scoped): profile id, coordinates, depth, soil type, linked `Site`.
  - `SoilLayer` (child): depth range and properties.
  - `SoilProfileImage` (child): file, description.
- CRUD: `profiles/`, `layers/`, `images/`.

### Floristics (`src/modules/bio/floristics/`)
- Purpose: manage custom floristic lists (not necessarily site-bound).
- Models:
  - `FloristicList` (user-scoped): name, description, timestamps.
  - `FloristicListItem` (child): plant `Species` reference with optional abundance/comment.
- CRUD: `lists/`, `items/`.

Notes:
- All user-scoped root entities have `user` and are filtered by the authenticated user.
- Child entities inherit scope via FK to parent (no separate `user` on children).
- Table names follow `bio_<domain>_<name>` convention; essential indexes and unique constraints are included.



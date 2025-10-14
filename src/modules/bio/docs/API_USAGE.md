## BIO API usage (frontend quick guide)

Auth: all endpoints require authentication. Pagination: PageNumber (`page`, `page_size`).

Base prefix: `/api/bio/` plus submodule prefixes below.

### Geobotany (`/api/bio/geobotany/`)
- `species/` GET (filters: `title`, `author`), POST, PUT/PATCH, DELETE
- `sites/` GET (user-scoped), POST, PUT/PATCH, DELETE
- `sites/<site_number>/<zone_type>/` GET, PUT/PATCH, DELETE (by composite key)
- `sites/<site_number>/<zone_type>/descriptions/` GET, POST, PUT, PATCH, DELETE
- `sites/<site_number>/<zone_type>/means/` GET (analytics)
- `sites/<site_number>/<zone_type>/distribution/` GET (analytics)
- `sites/<site_number>/<zone_type>/classification/` GET (analytics)
- `sites/custom-means/`, `sites/custom-distribution/`, `sites/custom-classification/` POST (analytics)
- `sites/comparison/`, `sites/custom-analysis/` POST (analytics)
- `descriptions/<description_id>/` DELETE

### Zoology (`/api/bio/zoology/`)
- `species/` GET (filters: `latin_name`, `author`, `title`), POST, PUT/PATCH, DELETE
- `populations/` GET (filters: `animal_species_id`, `site_id`), POST, PUT/PATCH, DELETE
- `observations/` GET (filters: `animal_species_id`, `site_id`, `population_id`), POST, PUT/PATCH, DELETE

### Ecoprofiles (`/api/bio/ecoprofiles/`)
- `profiles/` GET (filter: `name`), POST, PUT/PATCH, DELETE
- `profile-sites/` GET (filters: `profile_id`, `site_id`), POST, PUT/PATCH, DELETE

### Interactions (`/api/bio/interactions/`)
- `interactions/` GET (filters: `plant_species_id`, `animal_species_id`, `site_id`, `interaction_type`), POST, PUT/PATCH, DELETE

### Successions (`/api/bio/successions/`)
- `successions/` GET (filter: `site_id`), POST, PUT/PATCH, DELETE
- `stages/` GET (filter: `succession_id`), POST, PUT/PATCH, DELETE
- `stage-species/` GET (filters: `stage_id`, `plant_species_id`), POST, PUT/PATCH, DELETE

### Paleobotany (`/api/bio/paleobotany/`)
- `samples/` GET (filter: `sample_id`), POST, PUT/PATCH, DELETE
- `images/` GET (filter: `sample_id`), POST (multipart/form-data), PUT/PATCH, DELETE

### Geomorphology (`/api/bio/geomorphology/`)
- `profiles/` GET (filters: `profile_id`, `site_id`), POST, PUT/PATCH, DELETE
- `layers/` GET (filter: `profile_id`), POST, PUT/PATCH, DELETE
- `images/` GET (filter: `profile_id`), POST (multipart/form-data), PUT/PATCH, DELETE

### Floristics (`/api/bio/floristics/`)
- `lists/` GET (filter: `name`), POST, PUT/PATCH, DELETE
- `items/` GET (filters: `list_id`, `species_id`), POST, PUT/PATCH, DELETE

Notes:
- Root entities automatically set `user` on create; do not send it from frontend.
- File upload fields: send as `multipart/form-data`; other fields in JSON-serializable form.
- Standard pagination response structure is used by all list endpoints.



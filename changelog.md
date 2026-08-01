# Version 2026.7.2 (2026-08-01)

## What's Changed

### Fixed

- The easymode and profile extractors now decode HTML character references
  (`&auml;`, `&amp;`, `&nbsp;`, …) in display strings via `html.unescape`,
  matching what the translation extractor has always done. Regenerated the
  affected artifacts: 36 profile files (197 strings) and the easymode
  archive — every change is a decoded reference, a stripped tag, or an
  `&nbsp;` folded to a plain space. A parametrised test now asserts the
  property over every artifact.

### Added

- `Makefile` wrapping the common dev tasks (`make help` lists all targets).

# Version 2026.7.1 (2026-07-21)

## What's Changed

### Changed

- Regenerated `easymode_extract.json.gz`, `translation_extract.json.gz` and the
  `BLIND_VIRTUAL_RECEIVER`, `SHUTTER_VIRTUAL_RECEIVER` and
  `WATER_SWITCH_VIRTUAL_RECEIVER` profiles from the latest OCCU sources.
  Notable data changes: new `SHORT_OUTPUT_BEHAVIOUR` parameter in the
  water-switch profiles, `LONG_PROFILE_ACTION_TYPE` narrowed to a fixed
  value in the blind/shutter profiles, and revised German/English help
  texts and value labels in the translation extract.

# Version 2026.7.0 (2026-07-19)

## What's Changed

### Added

- New curated artifact `data/device_semantics.json` with a
  `device_semantics` accessor module: shared device classifications for
  downstream consumers. First classification: `doorbell_models`
  (`HM-Sen-DB-PCB`, `HmIP-DBB`, `HmIP-DSD-PCB`) — devices whose
  press/ring channel is a doorbell rather than a generic button, so
  aiohomematic/homematicip_local and openccu-loom map the ring press
  onto their platform's doorbell semantics (e.g. Home Assistant's
  standard `ring` event type) from one source of truth.

# Version 2026.6.1 (2026-06-27)

## What's Changed

### Fixed

- Restored the curated device-model labels for `HmIP-DLP`, `HmIP-UDI-SMI55`,
  `HmIP-SMO230` and `HmIP-SWDO-PL-2` in `translation_custom/device_models_{de,en}.json`.
  These models ship only as `device_icons` in the extract (no `device_models`
  entry), so without the curated overlay label they fall back to the raw model
  id in downstream consumers.

# Version 2026.6.0 (2026-06-27)

## What's Changed

### Changed

- Regenerated `easymode_extract.json.gz` and `translation_extract.json.gz`
  from the latest OCCU sources.

# Version 2026.5.0 (2026-05-10)

## What's Changed

### Changed

- Regenerated `easymode_extract.json.gz` and `translation_extract.json.gz`
  from the latest OCCU sources.

# Version 2026.4.1 (2026-04-24)

## What's Changed

### Added

- Initial release.
- Easymode metadata extractor (relocated from `aiohomematic/script/extract_ccu_easymodes.py`).
- CCU WebUI translation extractor (relocated from `aiohomematic/script/extract_ccu_translations.py`).
- Easymode link-profile extractor (relocated from `aiohomematic-config/script/parse_easymode_profiles.py`,
  python-dotenv dependency replaced with stdlib `_load_dotenv`).
- Vendored data artifacts (`easymode_extract.json.gz`, `translation_extract.json.gz`,
  `translation_custom/*.json`, `profiles/*.json.gz`) for downstream consumers.
- Per-receiver profile files written gzipped (`<RECEIVER>.json.gz`) for
  significantly smaller repository size while preserving lazy loading.
- Project documentation (`README.md`, `CLAUDE.md`, `NOTICE.md`).
- `.pre-commit-config.yaml` with ruff, codespell, bandit, yamllint, prettier,
  mypy.
- GitHub workflows: `test-run.yaml` (pytest + coverage), `pre-commit.yml`
  (prek hook validation), `release-on-tag.yml`, `python-publish.yml`.
- Bootstrap scripts (`script/setup`, `script/bootstrap`, `script/run-in-env.sh`).

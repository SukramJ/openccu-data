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

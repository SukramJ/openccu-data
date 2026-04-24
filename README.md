# openccu-data

Extract and distribute Homematic CCU configuration metadata
(translations, easymodes, link profiles) from
[OCCU](https://github.com/eq-3/occu) /
[OpenCCU](https://github.com/jens-maus/RaspberryMatic) /
[RaspberryMatic](https://github.com/jens-maus/RaspberryMatic).

This repository is the **single source of truth** for the data artifacts that
are consumed by [aiohomematic](https://github.com/sukramj/aiohomematic) and
[aiohomematic-config](https://github.com/sukramj/aiohomematic-config). Both
projects vendor the produced JSON archives at runtime.

## What this provides

| Extractor                      | Source                               | Output                                                                                 |
| ------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------- |
| `openccu-extract-easymodes`    | TCL config under `config/easymodes/` | `openccu_data/data/easymode_extract.json.gz`                                           |
| `openccu-extract-translations` | JS translation files + stringtable   | `openccu_data/data/translation_extract.json.gz` + `translation_custom/`                |
| `openccu-extract-profiles`     | TCL link-profile files per receiver  | `openccu_data/data/profiles/<RECEIVER_TYPE>.json.gz` (+ `_receiver_type_aliases.json`) |

All three read from either:

- a local OCCU/OpenCCU/RaspberryMatic checkout (`OCCU_PATH=/path/to/occu`), or
- a running CCU instance over HTTP/HTTPS (`CCU_URL=https://my-ccu.local`).

If both are set, the easymode/translation extractors merge results; the
profile extractor prefers the running CCU and falls back to local.

## Repository layout

```
openccu-data/
├── LICENSE                MIT (covers the code)
├── NOTICE.md              Data-artifact licensing (EQ-3/OCCU)
├── README.md              this file
├── CLAUDE.md              guide for AI assistants
├── changelog.md
├── pyproject.toml
├── openccu_data/
│   ├── const.py
│   ├── easymodes/extractor.py        easymode metadata parser
│   ├── translations/extractor.py     CCU WebUI translation parser
│   ├── profiles/extractor.py         easymode link-profile parser
│   └── data/                         committed, vendored output
│       ├── easymode_extract.json.gz
│       ├── translation_extract.json.gz
│       ├── translation_custom/*.json
│       └── profiles/*.json.gz (+ _receiver_type_aliases.json)
├── script/                           CLI wrappers
└── tests/
```

## Installation

```bash
python -m pip install -e .[test]
```

No third-party runtime dependencies; only the standard library.

## Usage

### Console scripts

After installation, three console scripts are available on the PATH:

```bash
OCCU_PATH=/path/to/occu openccu-extract-easymodes
OCCU_PATH=/path/to/occu openccu-extract-translations
CCU_URL=https://my-ccu.local openccu-extract-profiles
```

Output lands in `openccu_data/data/` by default. Override via `OUTPUT_DIR`.

### Without installation

```bash
OCCU_PATH=/path/to/occu python script/extract_easymodes.py
OCCU_PATH=/path/to/occu python script/extract_translations.py
CCU_URL=https://my-ccu.local python script/extract_profiles.py
```

### Environment variables

| Variable     | Purpose                                                                  |
| ------------ | ------------------------------------------------------------------------ |
| `OCCU_PATH`  | Path to a local OCCU/RaspberryMatic checkout                             |
| `CCU_URL`    | URL of a running CCU/OpenCCU instance (`http://` or `https://`)          |
| `OUTPUT_DIR` | Override the default output directory                                    |
| `RECEIVERS`  | (`extract_profiles` only) comma-separated list of receiver channel types |

`.env` files at the repository root are auto-loaded (existing env vars win).

## Vendoring into consumer projects

The committed artifacts in `openccu_data/data/` are the **source of truth**.
Consumers maintain their own runtime copies:

| Consumer              | Vendored copy                                                              |
| --------------------- | -------------------------------------------------------------------------- |
| `aiohomematic`        | `aiohomematic/ccu_data/easymode_extract.json.gz`                           |
| `aiohomematic`        | `aiohomematic/ccu_data/translation_extract.json.gz`                        |
| `aiohomematic`        | `aiohomematic/ccu_data/translation_custom/*.json`                          |
| `aiohomematic-config` | `aiohomematic_config/profiles/*.json.gz` (+ `_receiver_type_aliases.json`) |

After regenerating any artifact, copy the relevant files into the consumer
repository and open a PR there as well.

## Development

```bash
python -m pip install -e .[test]
pytest tests/
ruff check openccu_data/ tests/
mypy
```

## License

- **Code**: [MIT](./LICENSE).
- **Data artifacts** under `openccu_data/data/`: derivative of OCCU/RaspberryMatic
  and subject to the EQ-3 license (see [NOTICE.md](./NOTICE.md)). The curated
  `translation_custom/` overrides are MIT.

"Homematic" and "HomematicIP" are trademarks of eQ-3 AG. This project is not
affiliated with or endorsed by eQ-3 AG.

# openccu-data

Extract and distribute Homematic CCU configuration metadata
(translations, easymodes, link profiles, device images) from
[OpenCCU-Base](https://github.com/homematicip/OpenCCU-Base) /
[OpenCCU](https://github.com/OpenCCU/OpenCCU).

This repository is the **single source of truth** for the data artifacts that
are consumed by [aiohomematic](https://github.com/sukramj/aiohomematic) and
[aiohomematic-config](https://github.com/sukramj/aiohomematic-config). Both
projects vendor the produced JSON archives at runtime.

## What this provides

| Extractor                       | Source                               | Output                                                                                 |
| ------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| `openccu-extract-easymodes`     | TCL config under `config/easymodes/` | `openccu_data/data/easymode_extract.json.gz`                                           |
| `openccu-extract-translations`  | JS translation files + stringtable   | `openccu_data/data/translation_extract.json.gz` + `translation_custom/`                |
| `openccu-extract-profiles`      | TCL link-profile files per receiver  | `openccu_data/data/profiles/<RECEIVER_TYPE>.json.gz` (+ `_receiver_type_aliases.json`) |
| `openccu-extract-device-images` | PNGs under `config/img/devices/250/` | `openccu_data/data/device_images/250/` (byte-identical, incl. `coupling/`)             |

The first three read from either:

- a local OpenCCU-Base checkout (`OPENCCUBASE_PATH=/path/to/OpenCCU-Base`), or
- a running CCU instance over HTTP/HTTPS (`CCU_URL=https://my-ccu.local`).

Which source to use is not a free choice — see
[`DATA_SOURCES.md`](./DATA_SOURCES.md) for why a running CCU is currently
still required, and what has to change before it is not.

If both are set, the easymode/translation extractors merge results; the
profile extractor prefers the running CCU and falls back to local.

The device-image extractor reads a local checkout only (`OPENCCUBASE_PATH`).
It runs after the translation extractor: every filename in the `device_icons`
table of `translation_extract.json.gz` must exist in the copied tree, and a
missing one fails the run.

## Repository layout

```
openccu-data/
├── LICENSE                MIT (covers the code)
├── NOTICE.md              Data-artifact licensing (EQ-3/HMSL 2.0)
├── DATA_SOURCES.md        Where the artifacts come from; upstream transition
├── README.md              this file
├── CLAUDE.md              guide for AI assistants
├── AI_POLICY.md           AI contribution policy
├── changelog.md
├── Makefile               common dev tasks (`make help`)
├── pyproject.toml
├── openccu_data/
│   ├── const.py
│   ├── easymodes/extractor.py        easymode metadata parser
│   ├── translations/extractor.py     CCU WebUI translation parser
│   ├── profiles/extractor.py         easymode link-profile parser
│   ├── device_images/extractor.py    device image copier + device_icons check
│   └── data/                         committed, vendored output
│       ├── easymode_extract.json.gz
│       ├── translation_extract.json.gz
│       ├── translation_custom/*.json
│       ├── profiles/*.json.gz (+ _receiver_type_aliases.json)
│       └── device_images/250/*.png (+ coupling/*.png)
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

After installation, four console scripts are available on the PATH:

```bash
OPENCCUBASE_PATH=/path/to/OpenCCU-Base openccu-extract-easymodes
OPENCCUBASE_PATH=/path/to/OpenCCU-Base openccu-extract-translations
CCU_URL=https://my-ccu.local openccu-extract-profiles
OPENCCUBASE_PATH=/path/to/OpenCCU-Base openccu-extract-device-images
```

Output lands in `openccu_data/data/` by default. Override via `OUTPUT_DIR`.

### Without installation

```bash
OPENCCUBASE_PATH=/path/to/OpenCCU-Base python script/extract_easymodes.py
OPENCCUBASE_PATH=/path/to/OpenCCU-Base python script/extract_translations.py
CCU_URL=https://my-ccu.local python script/extract_profiles.py
OPENCCUBASE_PATH=/path/to/OpenCCU-Base python script/extract_device_images.py
```

### Environment variables

| Variable           | Purpose                                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCCUBASE_PATH` | Path to a local source checkout — `www/` (OpenCCU-Base) and `WebUI/www/` (OCCU) layouts both work; relative paths resolve against the repo root |
| `CCU_URL`          | URL of a running CCU/OpenCCU instance (`http://` or `https://`)                                                                                 |
| `OUTPUT_DIR`       | Override the default output directory                                                                                                           |
| `RECEIVERS`        | (`extract_profiles` only) comma-separated list of receiver channel types                                                                        |

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

The common tasks are wrapped in a `Makefile`:

```bash
make setup       # install dev dependencies + prek hooks
make test        # run the pytest suite
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy
make check       # lint + typecheck + test
```

`make help` lists all targets, including `make extract` /
`make extract-<name>` to regenerate the data artifacts. The same commands
also work without make:

```bash
python -m pip install -e .[test]
pytest tests/
ruff check openccu_data/ tests/
mypy
```

Parts of openccu-data are developed with agentic AI assistance, primarily
[Claude Code](https://www.anthropic.com/claude-code). Submitted issues are
also triaged and analyzed with agentic help. Every change is still reviewed
by a human maintainer and must pass the project's tests before it lands —
AI accelerates the work, it does not replace the review gate.

Contributions may use AI tools as well — see [AI_POLICY.md](./AI_POLICY.md)
for the rules that apply.

## License

- **Code**: [MIT](./LICENSE).
- **Data artifacts** under `openccu_data/data/`: derivative of OpenCCU-Base/OpenCCU
  and subject to the EQ-3 license (see [NOTICE.md](./NOTICE.md)). The curated
  `translation_custom/` overrides are MIT.

"Homematic" and "HomematicIP" are trademarks of eQ-3 AG. This project is not
affiliated with or endorsed by eQ-3 AG.

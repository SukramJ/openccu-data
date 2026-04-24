# NOTICE

This repository ships two distinct kinds of files that are governed by
different licenses. Please respect both when redistributing.

## 1. Original code (MIT License)

All Python source code in this repository — extractor modules, CLI entry
points, tests, and packaging metadata — is original work and licensed under
the [MIT License](./LICENSE).

This covers everything under:

- `openccu_data/` (except the `data/` subtree, see below)
- `script/`
- `tests/`
- top-level configuration files (`pyproject.toml`, `.pre-commit-config.yaml`,
  …)

## 2. Extracted data artifacts (EQ-3 / OCCU License)

The committed data artifacts under `openccu_data/data/` are derivative works
generated from the
[HomeMatic Open Central Control Unit SDK (HM-OCCU-SDK)](https://github.com/eq-3/occu)
maintained by eQ-3 AG, and from compatible distributions such as
[OpenCCU](https://github.com/jens-maus/RaspberryMatic).

Specifically these files:

- `openccu_data/data/easymode_extract.json.gz`
- `openccu_data/data/translation_extract.json.gz`
- `openccu_data/data/translation_custom/*.json` _(curated additions, MIT)_
- `openccu_data/data/profiles/*.json`

are obtained by parsing TCL configuration and JavaScript translation files
shipped with OCCU/RaspberryMatic. They retain the licensing of the original
upstream sources. Refer to OCCU's `LicenseDE.txt` for the full terms — in
short: free for private and non-commercial use; commercial redistribution
requires permission from eQ-3.

The `translation_custom/` files are the exception inside the data tree: they
contain hand-curated translation overrides authored by the openccu-data
maintainers and are released under the MIT License together with the rest of
the code.

## Trademarks

"Homematic" and "HomematicIP" are trademarks of eQ-3 AG. This project is not
affiliated with or endorsed by eQ-3 AG.

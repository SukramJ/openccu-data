# Data sources

Where the artifacts in `openccu_data/data/` actually come from, why a running
CCU is still involved, and what has to happen before extraction can be driven
entirely from a source checkout.

Measurements in this document were taken on 2026-08-28 against OpenCCU-Base at
commit `66b1211d` and a CCU running OpenCCU. They are reproducible with the
commands shown; re-check them before relying on them, since the upstream
situation is actively changing (see [Transition under way](#transition-under-way)).

## The three trees

Three repositories are easy to confuse. They are not interchangeable.

| Tree             | Upstream                              | Document root | Carries WebUI patches |
| ---------------- | ------------------------------------- | ------------- | --------------------- |
| **OpenCCU-Base** | `github.com/homematicip/OpenCCU-Base` | `www/`        | no                    |
| **OpenCCU**      | `github.com/OpenCCU/OpenCCU`          | — (none)      | yes, as patch files   |
| **Running CCU**  | the built firmware                    | `/` over HTTP | yes, applied          |

**OpenCCU-Base** is the eQ-3 base distribution. It has the full `www/` tree the
extractors read — `config/easymodes`, `config/stringtable_de.txt`,
`config/devdescr/DEVDB.tcl`, `webui/js/lang/` — and is a valid extraction
source on its own.

**OpenCCU** is a Buildroot build system, not a source tree. It has **no
extractable `www/`**; it holds 162 patch files under
`buildroot-external/patches/occu/` — 131 of which touch `WebUI/www` — and
pulls its base as a tarball:

```make
# buildroot-external/package/occu/occu.mk
OCCU_VERSION = 3.89.8-2
OCCU_SITE = $(call github,OpenCCU,occu,$(OCCU_VERSION))
```

Note the base is `OpenCCU/occu`, not OpenCCU-Base — and it uses the older
`WebUI/www/` layout.

**The running CCU** therefore serves `OpenCCU/occu` **plus** the applied
patches. This is the important point: the firmware is not OpenCCU-Base.

## Why the running CCU is still needed

Because the patches change the WebUI translations, and only the CCU has them
applied. Extracting from OpenCCU-Base alone loses what the patches add:

| Category        | OpenCCU-Base only | merged with CCU | contributed by CCU |
| --------------- | ----------------- | --------------- | ------------------ |
| `channel_types` | 183               | 234             | +51                |
| `ui_labels_de`  | 5276              | 5455            | +179               |
| `ui_labels_en`  | 5280              | 5458            | +178               |
| `device_icons`  | 535               | 535             | 0                  |

The added keys are traceable to individual patches. For example
`actionStatusControlLblNotActive`, one of the 179, exists in neither
`OpenCCU-Base/www/webui/js/lang/de/translate.lang.js` nor anywhere else under
`www/`, but is introduced by two patches:

```
buildroot-external/patches/occu/0122-WebUI-ProgramExecutionWithConditionCheck.patch:72
buildroot-external/patches/occu/0135-WebUI-Add-ControlPanel-AdvancedSettings.patch:839
```

The same shows up in file size — the patched copy the CCU serves is larger:

| File                                 | OpenCCU-Base | running CCU |
| ------------------------------------ | ------------ | ----------- |
| `webui/js/lang/de/translate.lang.js` | 67,882 B     | 82,321 B    |
| `.../translate.lang.extension.js`    | 83,037 B     | 85,546 B    |

Note that the merge does not fix everything. `load_sources_remote()` returns
empty dicts for `easymode_mappings`, `options_tcl_data`,
`profile_localization_data` and `easymode_option_values`
(`openccu_data/translations/extractor.py`), so for those four categories there
is no remote overlay and a local value always wins — even when the CCU has a
better one. See the first known deviation below for a case where this matters.

## Transition under way

Per the maintainer (2026-08-28): OpenCCU is switching its base from `occu` to
OpenCCU-Base, and the OpenCCU patches are to be integrated into OpenCCU-Base
directly rather than kept as a patch stack.

Once that lands, the distinction above collapses: OpenCCU-Base alone becomes
the correct source, and the running CCU is no longer needed for extraction.

**Until then, do not regenerate the artifacts from OpenCCU-Base.** It would
replace data describing the running firmware with data describing an
unpatched base — see the known deviations below.

### Known deviations (2026-08-28)

Two concrete values where OpenCCU-Base and the running firmware disagree.
Both are cases where the committed artifacts are the more accurate ones, and
both double as a progress indicator: when they agree, the WebUI patches have
landed in OpenCCU-Base.

**1. An untranslated placeholder.**

```
www/config/easymodes/WATER_SWITCH_VIRTUAL_RECEIVER/localization/en/GENERIC.txt:16
```

| OpenCCU-Base       | running CCU | committed artifact |
| ------------------ | ----------- | ------------------ |
| `"en* Durchfluss"` | `"Flow"`    | `"Flow"`           |

The `en*` prefix is an upstream translation placeholder. Because this value is
profile localization data, the remote overlay gap described above means
merging with a live CCU does **not** correct it.

**2. A narrowed constraint.**

```
www/config/easymodes/BLIND_VIRTUAL_RECEIVER/KEY_TRANSCEIVER.tcl:217
```

| OpenCCU-Base | running CCU | committed artifact |
| ------------ | ----------- | ------------------ |
| `{5 1}`      | `1`         | `fixed: 1`         |

Extracted as `constraint_type: "list"` versus `"fixed"`. The same difference
affects several sender types across `BLIND_VIRTUAL_RECEIVER` and
`SHUTTER_VIRTUAL_RECEIVER`.

Checking both is a `grep`, no tooling required:

```bash
grep -n wsmLinkOutputBehaviour \
  "$OPENCCUBASE_PATH"/www/config/easymodes/WATER_SWITCH_VIRTUAL_RECEIVER/localization/en/GENERIC.txt
grep -n 'PROFILE_3(LONG_PROFILE_ACTION_TYPE)' \
  "$OPENCCUBASE_PATH"/www/config/easymodes/BLIND_VIRTUAL_RECEIVER/KEY_TRANSCEIVER.tcl
```

## Target: generate on each OpenCCU release

The motivation for all of the above: if no running CCU is needed, the
artifacts can be generated automatically whenever OpenCCU cuts a release,
rather than by hand against someone's CCU.

This is **deliberately deferred** until the transition completes. Building it
today would mean checking out `OpenCCU/occu` at the pinned version and
replaying the patch stack — reimplementing part of the firmware build, for
machinery that is about to disappear.

After the transition, the same workflow needs only an OpenCCU-Base checkout at
the released revision, with no patch handling at all.

If it is ever needed before then, the shortcut is the firmware build itself:
Buildroot leaves the patched tree at `output/build/occu-<version>/WebUI/www`,
which is exactly what the CCU serves.

## What the extractors already support

Two properties are in place so that neither side of the transition requires a
code change:

**Both layouts are accepted.** Each extractor carries its own
`_resolve_www_root()` and picks whichever candidate actually holds `config/`:

- `<checkout>/www/` — OpenCCU-Base
- `<checkout>/WebUI/www/` — an `occu` tree, including the patched one the
  firmware build produces

Detection is by directory content, not by naming convention. Verified against
an empty directory, a tree matching neither shape aborts all three extractors
with a non-zero exit and writes no files — though the translation extractor
does so with an uncaught traceback rather than a clean message. Layout
detection itself is covered by `tests/test_www_root_resolution.py`.

**Output is reproducible.** All three extractors write gzip with `mtime=0` and
an empty filename field, so an unchanged input produces byte-identical files.
Without this, every run would produce a diff regardless of whether any data
changed — which would make an automated release workflow useless. Verified by
extracting the same source through both layouts, two seconds apart: all 68
output files identical.

## Related

- [`README.md`](./README.md) — usage and environment variables
- [`NOTICE.md`](./NOTICE.md) — licensing of the extracted artifacts
- [`CLAUDE.md`](./CLAUDE.md) — architecture notes for contributors

# CLAUDE.md - AI Assistant Guide for openccu-data

This document is the entry point for AI assistants working on the
`openccu-data` codebase. It is intentionally concise.

## Project Overview

`openccu-data` is the **data-extraction pipeline and source-of-truth
distribution** for Homematic CCU configuration metadata. It parses TCL and
JavaScript files from
[OpenCCU-Base](https://github.com/homematicip/OpenCCU-Base) /
[OpenCCU](https://github.com/OpenCCU/OpenCCU) into compact, typed
JSON artifacts that downstream Python libraries vendor at runtime.

### Key characteristics

- **Language**: Python 3.14+
- **Runtime dependencies**: stdlib only
- **License**: MIT for code; see [`NOTICE.md`](./NOTICE.md) for data licensing
- **Consumers**:
  - [`aiohomematic`](https://github.com/sukramj/aiohomematic) — vendors the
    `easymode_extract`/`translation_extract` archives + `translation_custom/`
  - [`aiohomematic-config`](https://github.com/sukramj/aiohomematic-config) —
    vendors `profiles/*.json` + `_receiver_type_aliases.json`

## Codebase layout

```
openccu_data/
├── const.py                       single source of truth for VERSION
├── data/                          committed extracted artifacts (source of truth)
│   ├── easymode_extract.json.gz
│   ├── translation_extract.json.gz
│   ├── translation_custom/        curated translation overrides (MIT)
│   ├── profiles/                  one .json.gz per receiver channel type
│   │   └── _receiver_type_aliases.json   (uncompressed; tiny, eager-loaded)
│   └── device_images/250/         byte-identical WebUI device PNGs (+ coupling/)
├── easymodes/extractor.py         TCL easymode parser → easymode_extract.json.gz
├── translations/extractor.py      JS + stringtable parser → translation_extract.json.gz
├── profiles/extractor.py          TCL profile parser → profiles/*.json
└── device_images/extractor.py     PNG copier → device_images/250/, checked against device_icons

script/                            CLI wrappers (sys.path shim → main())
tests/                             pytest suite
Makefile                           wrappers for the common commands (make help)
```

The four extractors are independent. They share no helper module; each is
self-contained and only depends on the standard library.

## Development environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[test]
```

### Common commands

```bash
pytest tests/                                       # run tests
pytest tests/ -v                                    # verbose
ruff check openccu_data/ tests/ script/             # lint
ruff format openccu_data/ tests/ script/            # format
mypy                                                # type-check
```

The `Makefile` wraps these (and more): `make test`, `make lint`,
`make format`, `make typecheck`, `make check` (lint + typecheck + test),
`make coverage`, `make prek`, `make extract-<name>`. `make help` lists all
targets. Targets run via `script/run-in-env.sh`, so an activated virtualenv
is not required.

### Console scripts

After `pip install -e .` four commands are on PATH:

```
openccu-extract-easymodes
openccu-extract-translations
openccu-extract-profiles
openccu-extract-device-images
```

All read `OPENCCUBASE_PATH` (local checkout), `CCU_URL` (running instance), and
optionally `OUTPUT_DIR` from the environment. `.env` at the repo root is
loaded by each `main()` (existing env vars win).

## Architecture notes

- **No runtime third-party deps.** Each extractor inlines a tiny
  `_load_dotenv()` so we don't pull in `python-dotenv`.
- **Output paths** default to `openccu_data/data/` resolved relative to the
  package directory (not the cwd) — so the scripts work regardless of where
  they are invoked from.
- **OPENCCUBASE_PATH resolution**: points at a local source checkout. Each
  extractor carries its own `_resolve_www_root()` and accepts both layouts in
  use: OpenCCU-Base keeps the document root at `www/`, an OCCU tree — including
  the patched one the OpenCCU firmware build produces — at `WebUI/www/`. The
  layout is picked by which candidate actually carries `config/`. Relative
  paths resolve against the repository root
  (`Path(__file__).parent.parent.parent`) in all extractors.
- **Merging**: `easymodes` and `translations` extractors merge results when
  both `OPENCCUBASE_PATH` and `CCU_URL` are set. `profiles` prefers `CCU_URL`
  and uses `OPENCCUBASE_PATH` as a fallback for empty results.

## Workflow / changelog

- Format: `YYYY.M.NN`
- Update both `openccu_data/const.py:VERSION` and `changelog.md` together.
- Branches: `main` is the default branch; PRs land here and releases are cut from it.

## When you regenerate an artifact

**Read [`DATA_SOURCES.md`](./DATA_SOURCES.md) first.** An upstream transition
is under way and regenerating from OpenCCU-Base alone currently _degrades_ the
artifacts; that document records which sources are valid and why.

1. Run the relevant `openccu-extract-*` command.
2. Diff `openccu_data/data/...` (be ready for large diffs in `*.json.gz`).
3. Commit the change in this repo with a description of the OpenCCU-Base
   revision / CCU firmware version that produced it.
4. **Sync to the vendored copies** in the consumer repos:
   - `aiohomematic/aiohomematic/ccu_data/`
   - `aiohomematic-config/aiohomematic_config/profiles/`

Open companion PRs in the consumer repos and reference the openccu-data
commit.

## Data licensing reminder

The files in `openccu_data/data/` (excluding `translation_custom/`) are
derivative works of OpenCCU-Base/OpenCCU and remain under their EQ-3
license (HMSL 2.0).
The Python _code_ is MIT. See [`NOTICE.md`](./NOTICE.md) before
redistributing.

## Which model does which work

Set by the owner for the go-fabric family on 2026-10-10 (go-fabric's
`CLAUDE.md`); the review split of 2026-11-08 (go-fabric #456) likewise.
Adopted here on 2026-11-08. A statement about the CCU firmware's metadata that
lands in this repo is cited later as fact — a comment that names a caller
or a consumer, a docstring that states what the other side does, a
`changelog.md` line — so the work that produces such statements gets
the strongest model, and the work a guard checks may use a cheaper one. The
agents in [Sub-Agent Delegation](#sub-agent-delegation) carry a default
model each; the rows below decide when a call overrides it (`model:` on the
Agent tool). Implementation defaults to Opus.

| Work                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Model                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Analysis, planning, reviews of design, audits; anything written into `DATA_SOURCES.md`, `NOTICE.md` or `changelog.md`, or a comment that names an OpenCCU-Base / OpenCCU file, a CCU translation or an easymode; the extractors that read a CCU (`CCU_URL`), the licence boundary of `openccu_data/data/` (eQ-3 HMSL 2.0, `NOTICE.md`); _which_ guard gets built and its bite line; rebases and merge conflicts where `main` may have overtaken the change                                                                                                                                                                                                                                                                                      | **Fable** (the default for this repo; also the `hunt` agent)    |
| Implementation of a finished plan with guards behind it: an extractor rule once the pattern exists, a test on an existing artefact, a `changelog.md` entry for a finished diff                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | **Opus** (the `impl` default; also what fast mode runs on)      |
| **Review of a slice's pull request, split (owner decision 2026-11-08, go-fabric #456).** The code review — correctness, concurrency, error paths, tests, the fixed report shape — is **Opus**. On top of it **Fable** reads, bounded: every new comment or docstring that names an OpenCCU-Base / OpenCCU file, a CCU translation or an easymode against OpenCCU-Base at the commit in `DATA_SOURCES.md`, the CCU reached through `CCU_URL`, every line that enters `DATA_SOURCES.md`, `NOTICE.md` or `changelog.md`, the paths of the first row, and the brief's decisions against the reference — the behavioural gaps a code review does not see. The load-bearing claims of the Opus review are verified before they reach the implementer. | **Opus**, then **Fable**                                        |
| Work a test or generator checks immediately: `make extract-*`, `ruff format`, `make prek`; search and first reading of a tree whose result a stronger model or the owner reads again                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | **Sonnet** (the `guard` default; `impl` with `model: "sonnet"`) |
| Mechanical inventories whose answer is a list the caller can re-grep: which files reference X, which links are dead, which entries lack a counterpart                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | **Haiku** (`sweep` default)                                     |

Sonnet never writes a claim about an OpenCCU-Base / OpenCCU file, a CCU translation or an easymode into the repo, and
never touches the paths named in the first row. Haiku returns lists, never
verdicts. When in doubt about which row a task is in, it is in the first.

---

## Sub-Agent Delegation

As go-fabric's and openccu-loom's rule (owner, 2026-10-10). The main
conversation owns planning, contract and wire decisions, guard
specifications, sub-agent steering, and final verification. It does not own
typing.

**Delegate what a gate can prove; keep what only a reader can accept.**
Delegate freely: table cases, fakes, scaffolding, fixture updates, doc and
link cleanups, version bumps across the changelog set, inventories and grep
sweeps. Never delegate: the extractor rules, `DATA_SOURCES.md`, the licence boundary, and _which_ guard gets
built. Locating is delegable; reading is not.

| Agent   | Default model | Use for                                                     |
| ------- | ------------- | ----------------------------------------------------------- |
| `impl`  | Opus          | scoped implementation with a stated acceptance command      |
| `guard` | Sonnet        | tests from a caller-written guard spec, plus the bite proof |
| `sweep` | Haiku         | read-only inventories and grep sweeps, high fan-out         |
| `hunt`  | Fable         | adversarial read-only defect hunt, ranked candidates        |

Each default is one row of
[Which model does which work](#which-model-does-which-work); a call that
falls into another row passes `model:` on the Agent tool — `impl` with
`model: "sonnet"` for work a generator or formatter checks immediately.

**Size CPU-bound fan-out from the host, never from a constant** — the owner
works from a 4-core box and a 14-core box:

```sh
cores=$(nproc); agents=$(( (cores - 1) / share ))   # share = cores per agent
```

Check the 1-minute load first; if it is at or above the core count, run one
CPU-bound agent and queue the rest. Eight concurrent agents is a practical
ceiling whatever the core count. Every CPU-bound agent must **pin** its share
in the command it runs (`pytest tests/<area>` — one process is one core; never a parallel run from a sub-agent) — handing out a number without
pinning it changes nothing. Read-only agents cost no core worth counting;
6–8 is a practical ceiling there.

Two hard rules: **no sub-agent runs the full gate (`make check` (lint, typecheck, tests)) or a
repo-wide lint** — the full gate runs once, in the main conversation, at the
end of the slice — and **no two writing agents in the same package**
(disjoint file sets, or `isolation: "worktree"`).

Every brief carries five things: the files and public surface plus one style
reference; the acceptance command the agent runs itself; the invariants it
touches; **stop conditions** (new dependency, API or wire change, credential
handling, an ADR-shaped decision — a stop is a successful outcome); and a
report format ≤ 250 words, large artefacts to the scratchpad as a path.

**A report is a claim.** Read the diff, run the gate yourself. For `guard`,
the acceptance artefact is not a green test but the **bite proof**: the named
production line removed, the test observed red with its message, the line
restored, green again.

---

## Token use

Set by the owner on 2026-10-14 (efficient use of the tokens matters to the
owner), as go-fabric's rule of the same date. A slice costs on
the order of half a million to a million tokens per implementing agent
before the owner's review; the rules below are what keeps that from
doubling.

- **Read slices, not files.** `sed -n a,bp`, `grep -n` with a tight
  pattern and `head`; a whole file only when the task is the file. Never
  re-read what is already in context; cite the earlier read.
- **Delegate first reads.** A source tree's inventory (OpenCCU-Base, OpenCCU, aiohomematic, this repo)
  is a `sweep` or Sonnet read written to the scratchpad with `file:line`
  for every fact; the owner spot-checks the load-bearing lines and verifies
  every fact about the CCU firmware's metadata before it enters a brief or
  `DATA_SOURCES.md`, `NOTICE.md` or `changelog.md` — the agent's result is a map, never a citation.
- **Logs by their summary.** The gate (`make check` (lint, typecheck, tests)) runs in the
  background with a summary file (one line per gate, `FAIL`/`ok` lines
  only); read the summary, and open a log only on failure, with `grep` for
  the failure markers and the error strings — never `cat`. The same for CI:
  the job log is fetched once to a file and grepped.
- **One turn, every independent call.** Reads, checks and background
  starts that do not depend on each other go out together; a wait is a
  `Monitor` or an `until` loop in the background, not polling by hand.
- **Short artefacts.** A brief names files, decisions and the acceptance
  command, not prose; a report follows the fixed shape of
  [Sub-Agent Delegation](#sub-agent-delegation) (≤ 250 words, large
  artefacts as a scratchpad path); status messages to the owner are short,
  outcome first, in German.
- **Skip what cannot have changed.** No regeneration for a comment change;
  no second gate run for a notes-only commit — say what was skipped and
  why.
- **Edit by script.** Several replacements in several files are one
  scripted call with asserted anchors, not a chain of interactive edits;
  a generated file (`openccu_data/data/`) is regenerated, never patched.
- **Agents read what the brief names.** An implementing agent gets the
  file list and the pinned sources in the brief, reads those, and reports
  in the fixed shape; it does not survey the tree. One agent per brief;
  two agents only on disjoint paths, at most one Opus agent at a time.
- **Push, pull request and tag are the session's own calls.** An
  implementing agent works locally — branch, commits, guards — and
  reports; the owner's session reads the diff, runs the gate, pushes,
  opens the pull request and tags the merge commit; the owner merges. A
  delegated push, pull request or tag is refused by the auto-mode
  classifier ("Create Public Surface", 2026-11-07), and the review in
  [Which model does which work](#which-model-does-which-work) sits
  between the agent's report and the push anyway.

---

## Tips for AI assistants

### Do

- ✅ Keep the extractors stdlib-only.
- ✅ Match the existing style (regex constants at top, helpers below, `main()`
  at the bottom, `if __name__ == "__main__":` block).
- ✅ Update tests when changing parsing logic; tests live next to the
  extractor they cover.
- ✅ Update `NOTICE.md` if a new artifact is added to `data/`.
- ✅ Bump `VERSION` and `changelog.md` for any user-visible change.

### Don't

- ❌ Add runtime third-party dependencies — keep it stdlib.
- ❌ Skip the consumer-repo sync after regenerating artifacts.
- ❌ Touch `data/` files by hand — always regenerate via an extractor.
- ❌ Write archives with plain `gzip.open()` — pass `mtime=0` and an empty
  filename so an unchanged input yields byte-identical output.
- ❌ Move modules without updating the console-script entry points in
  `pyproject.toml`.

## When in doubt

1. Read the relevant extractor's module docstring.
2. Look at how the consuming project loads the artifact
   (`aiohomematic/ccu_translations.py`, `aiohomematic/easymode_data.py`,
   `aiohomematic_config/profile_store.py`).
3. Run the tests.

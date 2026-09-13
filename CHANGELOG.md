# Changelog

All notable changes to aloeschema are recorded here.

Generated from `CHANGELOG.yaml`, which is the source of truth --
edit that file, then run `technoproj-changelog generate`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

aloeschema vendors a snapshot of the schema.org ontology. Which release
that is, is RECORDED rather than encoded: every entry from 0.3.0 carries a
`schemaorg_release` field, `src/data/release.py` holds the same release and
a fingerprint of the graph, and `script/checks.py` fails the build when the
two disagree. aloeschema's own version says nothing about schema.org's.

## [0.3.3] - 2026-09-13

`v0.3.3` &middot; schema.org `30.0`

`registerCustomProperty` accepts datatype ranges again.

It rejected every one of them -- `Text`, `Number`, `Boolean`, `Date`,
`DateTime` -- with `PROPERTY_RANGE_TYPE_NOT_RECOGNIZED`, which is the
second example in the README. Only class ranges worked. The bug dates
from when enumeration support went in; it was invisible because no
test registered a property with a datatype range, and the README
example that does could not run at all until 0.3.2 shipped the data.

### Added

- `tests/test_readme.py` executes both README examples and covers
  datatype ranges, class ranges and unknown ranges. Both bugs fixed
  in 0.3.2 and 0.3.3 were on that path and neither was covered.

### Fixed

- The range guard raises only when the range is neither a valid type
  nor a valid value type, which is what its error message says. It
  used `or`, and because `IsValidValueType` is a subset of
  `IsValidType`, a valid `Text` range satisfied the second arm and
  raised. The code immediately below it records datatype ranges in
  `properties[name]["datatype"]`, which the guard made unreachable.


## [0.3.2] - 2026-09-12

`v0.3.2` &middot; schema.org `30.0`

The first release whose wheel contains the schema.org data.

`aloeschema.data` was missing from every wheel and sdist ever
published, so `load_schema_org()` raised `ModuleNotFoundError` on any
`pip install` -- the first example in the README, broken since at
least 0.2.0. Anyone who hit it was not doing anything wrong.

Editable installs were unaffected, which is why it went unnoticed:
`pip install -e .` resolves the package straight from `src/`, so the
test suite passed against the source tree while the artifact it
produced did not work.

### Added

- The release pipeline installs the built wheel into a clean
  environment and calls `load_schema_org()` through it before
  publishing. Verified against the published 0.3.1 wheel, which it
  rejects.
- `tests/test_packaging.py` fails when a package directory under
  `src/` is missing from the declared package list, catching the same
  defect at test time.

### Fixed

- `[tool.setuptools].packages` declares `aloeschema.data`. setuptools
  does not imply subpackages from their parent, and only the parent
  was listed.


## [0.3.1] - 2026-09-12

`v0.3.1` &middot; schema.org `30.0`

A release-pipeline fix. No library code changed between 0.3.0 and
0.3.1, and the vendored ontology is the same schema.org 30.0.

0.3.0 is on GitHub but never reached PyPI, which is why PyPI skips
from 0.2.3 to 0.3.1. Its upload was refused with `invalid-publisher`:
PyPI's trusted publisher is a tuple of owner, repository, workflow
filename and environment, and the release workflow had been renamed
from `publish.yml` to `release.yml`, which revoked the grant. Every
other claim matched. Nothing was published, so no version was spent.

### Fixed

- The release workflow is `publish.yml` again, the filename PyPI is
  configured for, and says at the top of the file that its name is
  load-bearing. The constraint was invisible, which is what made the
  rename look free.
- `BUILDINFO.txt` records the default branch rather than whichever
  branch sorts first alphabetically. A released commit is normally on
  both `main` and the branch it was developed on, so 0.3.0 shipped
  `branch: claude/charming-mayer-foqboi` despite being released from
  `main`.


## [0.3.0] - 2026-09-12

`v0.3.0` &middot; schema.org `30.0`

The vendored schema.org snapshot is now a pinned, named, verifiable
release. Before this, it was an unreproducible capture of
`version/latest` taken partway through schema.org's 30.0 development
window: it matched no published release, carried two synthetic root
nodes present in no release at all, and nothing anywhere recorded
which ontology it was.

### Added

- `schemaorg_release` is recorded on every release from here on, in the
  changelog entry and in `BUILDINFO.txt`, and `src/data/release.py`
  carries it alongside a fingerprint of the ontology graph.
- `load_schema_org()` returns `schemaorg_release` in its result dict.
- `script/vendor_schemaorg.py` regenerates the snapshot from a pinned
  release, so it can be reproduced and verified rather than trusted.
- `script/checks.py` fails the build when the snapshot, the recorded
  release and the changelog entry disagree.

### Changed

- The vendored ontology is schema.org release 30.0. Relative to the
  capture it replaces this adds 34 terms -- among them
  `schema:Credential`, `schema:jobDuration` and the DE and IT nonprofit
  enumerations -- and drops two synthetic root nodes that were never
  part of schema.org. Net: one more type, eighteen more properties, one
  fewer enumeration. More input validates than before, which is why
  this is a minor rather than a patch.
- `load_schema_org(fetch=True)` now warns with `SchemaOrgReleaseWarning`
  when what it fetched is not the vendored release. schema.org publishes
  no version marker inside the JSON-LD, so an unrecognised document
  reports `schemaorg_release: None` rather than guessing.
- Release tooling is the shared technoproj engine, and versions follow
  the Aloecraft scheme in `doc/ALIGNMENT.md`.


## [0.2.3] - 2026-06-30

`v0.2.3`

Requires Python 3.11 or newer.


## [0.2.2] - 2026-06-30

`v0.2.2`

Tests moved to `tests/`, and README badges added.


## [0.2.1] - 2026-06-30

`v0.2.1`

Packaging fix; same tree as 0.2.0.


## [0.2.0] - 2026-06-30

`v0.2.0`

Enumeration support: `registerCustomEnumeration`,
`registerCustomEnumerationValue`, `IsEnumerationType` and
`EnumerationValueIsOfType`.

No `schemaorg_release` is recorded for this release or any before it.
The ontology these shipped was a capture of `version/latest` taken in
January 2026, between schema.org 29.3 and 30.0, and it corresponds to
no published release -- so there is no release to name. That is the
defect 0.3.0 fixes.

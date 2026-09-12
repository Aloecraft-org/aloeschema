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

## [0.3.0] - unreleased

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

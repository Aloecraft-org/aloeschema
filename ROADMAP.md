# aloeschema Roadmap

## Why this project exists

Schema.org is a rare asset for agent work: roughly 1,000 types and 1,650 properties
with real domain/range semantics that every frontier model already absorbed during
pretraining. Most agent frameworks invent an ad-hoc type vocabulary and then spend
their prompt budget teaching it. aloeschema borrows a shared one for free, and lets
you extend it where your domain needs terms schema.org does not have.

The roadmap below moves from "correct" to "as advertised" to "portable", in that
order. Each stage is shippable on its own.

---

## Stage 1 — Correctness, quality, and build

**Goal:** the package on PyPI installs and works, the code does what it claims, and
CI catches the classes of defect that got us here.

**Status:** in progress

### Build and packaging

- [ ] Include `aloeschema.data` in the wheel. `pyproject.toml` declares
      `packages = ["aloeschema"]`, so `src/data/` is excluded from the built
      distribution and `load_schema_org()` raises `ModuleNotFoundError` for every
      user who installs from PyPI. CI does not catch this because it installs with
      `pip install -e .`, which resolves against the source tree.
- [ ] Raise the build-system `setuptools` floor to `>=77`. The PEP 639
      `license = "apache-2.0"` string is not understood by setuptools 68 and fails
      the build with a schema validation error.
- [ ] Fix `[tool.pytest.ini_options] testpaths`, which points at `test` — a
      directory that does not exist. Bare `pytest` currently collects nothing.
- [ ] Make `requests` an optional dependency. It is a hard requirement today but is
      only used by the `load_schema_org(fetch=True)` path.
- [ ] Add a CI job that builds the wheel, installs it into a clean environment, and
      runs the README examples against it. This is the specific check that would
      have caught the packaging bug.

### Correctness

- [ ] `registerCustomType` aliases the parent's ancestry list instead of copying it,
      so registering a child mutates its parent in place:
      `Person` becomes `['Thing', 'Person', 'User']`, and `TypeDescendantOf('User',
      'Person')` returns `True`. Sibling registrations compound the corruption. This
      breaks the feature the library exists to provide.
- [ ] `registerCustomProperty` has an inverted range guard
      (`if not IsValidType(x) or IsValidValueType(x)`), so every valid datatype range
      is rejected. The `registerCustomProperty` example in the README raises.
- [ ] Model the type hierarchy as the DAG it actually is. `_extract_types` follows
      only the first parent, discarding multiple inheritance for the 57 types that
      declare more than one parent. 84 types end up unreachable from `Thing`, so
      `Certification` cannot have a `name` and `Diet` cannot have `overview`.
      Replace the single `path` list with a transitively-closed ancestor set.
- [ ] `AloeSchemaError` extends `BaseException`, so it escapes `except Exception:`
      in calling code. It should extend `Exception`.
- [ ] `IsValidType` / `IsValidPropertyType` are annotated `-> bool` but return a
      dict or `None`.
- [ ] `_extract_types` is O(n²): it does a linear scan over the whole graph inside a
      `while` loop. The ancestor-set rewrite should fix this as a side effect.

### Code quality

- [ ] Remove triplicated definitions. `validator.py`, `__init__.py`, and
      `tests/test_unit.py` each contain three copies of the same functions. Python's
      last-definition-wins makes this invisible at runtime — except in the test file,
      where it means two of the three enumeration tests never execute.
- [ ] Remove the module-level `TextTestRunner` call in `tests/test_unit.py`, which
      runs the suite a second time at import.
- [ ] Add assertions to `test_inheritsAncestorProperties`, which currently asserts
      nothing.
- [ ] Add `ruff` to CI with `F811` (redefinition) enabled — the rule that flags the
      duplication above.

---

## Stage 2 — Working as advertised

**Goal:** a Python library where imperative schema construction is solid, and the
same extensions can be expressed as a document. Both paths are first-class.

### Dual extension model

The imperative API stays as the primary ergonomic surface. Nothing about the
`registerCustomType` / `registerCustomProperty` / `registerCustomEnumeration`
workflow goes away or becomes a second-class wrapper.

Alongside it, the same extensions become expressible as a declarative document:

```json
{
  "aloeschema": "1.0",
  "extends": "schemaorg/29.0",
  "prefix": { "acme": "https://acme.example/ns#" },
  "types": [
    { "name": "acme:User", "subClassOf": "schema:Person",
      "comment": "An authenticated account holder." }
  ],
  "properties": [
    { "name": "acme:userName", "domain": ["acme:User"], "range": ["schema:Text"] }
  ],
  "enumerations": [
    { "name": "acme:TaskStatus", "values": ["Active", "Pending"] }
  ]
}
```

- [ ] Define the extension document format. Shape it as valid JSON-LD (custom types
      as `rdfs:Class` with `rdfs:subClassOf`) so it is the same syntax schema.org
      already publishes — no new vocabulary for a model to learn.
- [ ] `load_extension(schema, doc)` — apply a document to a schema.
- [ ] `dump_extension(schema)` — serialize the custom terms registered so far back
      out to a document.
- [ ] Round-trip equivalence: a schema built imperatively, dumped, and reloaded must
      be identical to the original. This is the property test that keeps the two
      paths honest, and it belongs in the conformance suite in Stage 3.

### Data and metadata

- [ ] Move the compiled schema out of `src/data/schemaorg_current.py` — a 30,844-line
      Python `dict` literal — and into a JSON resource loaded via
      `importlib.resources`. Data should be data. This also cuts import cost and is a
      prerequisite for every non-Python consumer.
- [ ] Retain `rdfs:comment` in the compiled index. The natural-language descriptions
      are the single most useful thing to hand an LLM, and the current index drops
      them (types keep only `path`/`properties`/`children`).
- [ ] Pin and record the schema.org version. The vendored snapshot carries no version
      marker at all, so builds are not reproducible and users cannot target a
      specific release.
- [ ] Namespace custom terms. A bare `User` collides with any future schema.org
      `User`, and two teams' extensions cannot be merged. Give extensions a prefix
      and IRI.
- [ ] Settle mutation semantics. `registerCustomType` returns a dict but also mutates
      its input; the tests' `.copy()` is shallow and protects nothing. Pick one
      contract and document it.

### Documentation

- [ ] Every README and `quickstart.ipynb` example verified against a clean install
      in CI, so documentation drift becomes a build failure.

---

## Stage 3 — Specification and conformance suite

**Goal:** make correctness portable, so a port can be proven equivalent rather than
assumed equivalent.

- [ ] Write `SPEC.md`: the compiled schema format, the extension document format,
      and the validation semantics — DAG ancestry, case-folding rules, enumeration
      membership, domain/range inheritance.
- [ ] Publish a language-agnostic conformance suite as JSON (`conformance/*.json`),
      each case a `{input, expected}` pair. The existing Python tests are most of the
      content; they need to move from assertions into data.
- [ ] Run the Python implementation against the suite in CI.
- [ ] Publish the compiled schema JSON as a release asset so every implementation
      consumes a byte-identical artifact instead of re-deriving it.

---

## Stage 4 — Portability by protocol

**Goal:** every language gets aloeschema without anyone writing a port.

- [ ] A CLI with JSON in and JSON out:
      `aloeschema validate --subject Person --property knowsAbout --object Thing`.
      Any language can shell out to this today.
- [ ] An MCP server exposing `validate_triple`, `properties_for_type`,
      `describe_type`, and `register_custom_type`. Since the point of the project is
      easier collaboration with agents, MCP is the natural distribution channel —
      and it sidesteps port maintenance entirely.
- [ ] JSON Schema emission: `aloeschema jsonschema acme:User` produces a JSON Schema
      derived from the type's properties and ranges, ready to drop into a tool
      definition or a structured-output `response_format`. This closes the loop —
      schema.org supplies a vocabulary the model already knows, and JSON Schema is
      how you actually constrain what it emits. Today the library can only tell you a
      triple was valid after the fact; this constrains generation before it happens.

---

## Stage 5 — Language ports

**Goal:** native implementations where the protocol boundary is too expensive.

- [ ] TypeScript first — the largest agent ecosystem, and it runs in Node, the
      browser, and edge runtimes. With the compiled JSON and the conformance suite in
      place this is a small implementation.
- [ ] Go and/or Rust, driven by actual demand rather than speculation.
- [ ] A Rust core compiled to WASM is the theoretical endgame, but MCP plus a
      TypeScript port likely covers the overwhelming majority of real usage. Revisit
      only if that assumption proves wrong.

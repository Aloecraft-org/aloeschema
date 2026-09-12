# Copyright (C) Michael Godfrey 2026 | aloecraft.org <michael@aloecraft.org>
# Licensed under the Apache License, Version 2.0.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
"""aloeschema's own consistency invariants, for the technoproj engine.

The generic half -- "pyproject.toml holds the version the changelog implies"
-- is `stamps` in .technoproj. This is the half that does not generalise: the
vendored schema.org snapshot, and the release it claims to be.

What it guards. The snapshot that preceded release 30.0 was an
unreproducible capture of `version/latest` taken mid-development: it matched
no published release, carried two synthetic root nodes present in no release
at all, and nothing recorded which ontology it was. The fix is that the
release is now recorded -- and a recorded fact is only worth anything if
something checks it, which is this.

Offline and import-free by design: the modules are loaded from their paths,
so the check runs in CI without the package installed and without the
engine depending on aloeschema.
"""

import os


def _module(root, relpath):
    """Load a data module straight from its source, into a fresh namespace.

    Compiled here rather than imported, for two reasons. The data modules
    import nothing beyond the standard library, so this needs neither an
    installed aloeschema nor its dependencies. And the import machinery
    caches bytecode by mtime at one-second granularity, so an edit made in
    the same second as the last import is read back stale -- which would
    make this check pass against a file that had already changed.
    """
    path = os.path.join(root, relpath)
    ns = {"__name__": "_aloeschema_check", "__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)  # noqa: S102
    return ns


def consistency(doc, ctx):
    bad = []
    root = ctx["root"]

    try:
        data = _module(root, "src/data/__init__.py")
        rel = _module(root, "src/data/release.py")
        snap = _module(root, "src/data/schemaorg_current.py")
    except Exception as e:
        return ["src/data: cannot load the vendored snapshot (%s)" % e]

    # 1. The snapshot is the release release.py says it is. Both files are
    #    generated together, so a mismatch means one was edited by hand.
    got = data["graph_fingerprint"](snap["schemaorg_current_jsonld"])
    if got != rel["SCHEMAORG_GRAPH_SHA256"]:
        bad.append(
            "src/data/schemaorg_current.py does not match the release recorded "
            "in src/data/release.py (%s): graph fingerprint is %s, expected %s. "
            "Regenerate both with script/vendor_schemaorg.py."
            % (rel["SCHEMAORG_RELEASE"], got[:16], rel["SCHEMAORG_GRAPH_SHA256"][:16])
        )

    # 2. The newest changelog entry records the same release the code ships.
    #    This is the fact a consumer reads off a release, so it is the one
    #    that must not drift from the tree.
    newest = doc["releases"][0]
    claimed = newest.get("schemaorg_release")
    if claimed is None:
        bad.append(
            "CHANGELOG.yaml: newest entry (%s) is missing schemaorg_release; "
            "every entry records which schema.org release it ships"
            % newest.get("version")
        )
    elif str(claimed) != rel["SCHEMAORG_RELEASE"]:
        bad.append(
            "CHANGELOG.yaml: newest entry (%s) says schemaorg_release %s but "
            "src/data/release.py ships %s"
            % (newest.get("version"), claimed, rel["SCHEMAORG_RELEASE"])
        )

    return bad

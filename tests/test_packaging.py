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
"""Guards on what actually ships, as opposed to what the tests can import.

Every wheel and sdist up to 0.3.1 omitted `aloeschema.data`, so
`load_schema_org()` raised ModuleNotFoundError on any non-editable install
-- the README's first example, broken for months. It survived because CI
installs with `pip install -e .`, which resolves the package straight from
`src/`: the suite passed against the source tree and nothing exercised the
artifact.

The pipeline's real guard is installing the built wheel into a clean
environment before publishing. This is the cheap half, catching the root
cause at test time.
"""

import pathlib
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestPackaging(unittest.TestCase):
    def test_theDataSubpackageIsImportable(self):
        """Fails loudly wherever the suite runs, source tree or installed."""
        from aloeschema.data import graph_fingerprint  # noqa: F401
        from aloeschema.data.release import SCHEMAORG_RELEASE

        self.assertTrue(SCHEMAORG_RELEASE)

    def test_everyPackageDirectoryIsDeclared(self):
        """setuptools does not imply subpackages from their parent, so each
        one has to be listed. This compares the list against the tree."""
        pyproject = ROOT / "pyproject.toml"
        if not pyproject.is_file():
            self.skipTest("not running from a source checkout")

        cfg = tomllib.load(pyproject.open("rb"))["tool"]["setuptools"]
        declared = set(cfg["packages"])

        src = ROOT / "src"
        found = {"aloeschema"} | {
            "aloeschema." + p.parent.relative_to(src).as_posix().replace("/", ".")
            for p in src.rglob("__init__.py")
            if p.parent != src
        }
        self.assertEqual(
            found - declared,
            set(),
            "package directories exist under src/ but are not in "
            "[tool.setuptools].packages, so they will be missing from the "
            "wheel and the sdist",
        )


if __name__ == "__main__":
    unittest.main()

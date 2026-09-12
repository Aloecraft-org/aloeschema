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

import copy
import unittest
import unittest.mock
import warnings

import aloeschema
from aloeschema import load_schema_org
from aloeschema.data import graph_fingerprint
from aloeschema.data.release import SCHEMAORG_GRAPH_SHA256, SCHEMAORG_RELEASE
from aloeschema.data.schemaorg_current import schemaorg_current_jsonld
from aloeschema.error import SchemaOrgReleaseWarning


class TestVendoredRelease(unittest.TestCase):
    def test_snapshotMatchesTheRecordedFingerprint(self):
        """The two generated files must not drift. script/checks.py enforces
        this at release time; this catches it at test time."""
        self.assertEqual(
            graph_fingerprint(schemaorg_current_jsonld), SCHEMAORG_GRAPH_SHA256
        )

    def test_loadSchemaOrg_reportsTheRelease(self):
        self.assertEqual(load_schema_org()["schemaorg_release"], SCHEMAORG_RELEASE)

    def test_snapshotCarriesTerms_addedIn30(self):
        """Present in release 30.0 and absent from the capture it replaced,
        so this fails if the old snapshot ever comes back."""
        types = load_schema_org()["types"]
        self.assertIn("Credential", types)
        self.assertIn("DENonprofitType", types)

    def test_snapshotHasNoSyntheticRootNodes(self):
        """`rdfs:Class` and `rdf:Property` were injected by the old vendoring
        step and appear in no published schema.org release."""
        ids = {n["@id"] for n in schemaorg_current_jsonld["@graph"] if "@id" in n}
        self.assertNotIn("rdfs:Class", ids)
        self.assertNotIn("rdf:Property", ids)

    def test_fingerprintIgnoresListOrder(self):
        """schema.org and the schemaorg repository publish one and the same
        release with `domainIncludes` members in different orders. The
        fingerprint identifies the ontology, not the serialisation."""
        shuffled = copy.deepcopy(schemaorg_current_jsonld)
        for node in shuffled["@graph"]:
            for key, value in node.items():
                if isinstance(value, list):
                    node[key] = list(reversed(value))
        self.assertEqual(graph_fingerprint(shuffled), SCHEMAORG_GRAPH_SHA256)

    def test_fingerprintSeesATermChange(self):
        tampered = copy.deepcopy(schemaorg_current_jsonld)
        tampered["@graph"][0] = dict(tampered["@graph"][0], **{"@id": "schema:Nope"})
        self.assertNotEqual(graph_fingerprint(tampered), SCHEMAORG_GRAPH_SHA256)


class TestFetchMismatch(unittest.TestCase):
    def _fetching(self, payload):
        response = unittest.mock.Mock()
        response.json.return_value = payload
        return unittest.mock.patch.object(
            aloeschema.requests, "get", return_value=response
        )

    def test_fetchMatchingTheSnapshot_reportsTheReleaseAndDoesNotWarn(self):
        with self._fetching(copy.deepcopy(schemaorg_current_jsonld)):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                result = load_schema_org(fetch=True)
        self.assertEqual(result["schemaorg_release"], SCHEMAORG_RELEASE)
        self.assertEqual(
            [w for w in caught if issubclass(w.category, SchemaOrgReleaseWarning)], []
        )

    def test_fetchOfAnUnknownOntology_warnsAndReportsNoRelease(self):
        other = copy.deepcopy(schemaorg_current_jsonld)
        other["@graph"] = [
            n for n in other["@graph"] if n.get("@id") != "schema:Credential"
        ]
        with self._fetching(other):
            with self.assertWarns(SchemaOrgReleaseWarning):
                result = load_schema_org(fetch=True)
        self.assertIsNone(result["schemaorg_release"])


if __name__ == "__main__":
    unittest.main()

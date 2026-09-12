# Copyright (C) [2026] [michael@aloecraft.org]
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

import hashlib
import json


def _canonical(node):
    """Order-insensitive form of a JSON-LD value.

    Every list in the schema.org vocabulary is a set -- `domainIncludes`,
    `rangeIncludes`, `subClassOf`, `@type`. Two publishers of one and the
    same release order them differently: 491 of 30.0's 3,219 nodes differ
    between schema.org and the schemaorg repository on list order alone, with
    identical members. Sorting makes the fingerprint identify the ontology
    rather than one publisher's serialisation of it.
    """
    if isinstance(node, dict):
        return {k: _canonical(v) for k, v in sorted(node.items())}
    if isinstance(node, list):
        items = [_canonical(v) for v in node]
        return sorted(items, key=lambda v: json.dumps(v, sort_keys=True))
    return node


def graph_fingerprint(data):
    """Identify a schema.org document by its terms.

    schema.org publishes no version marker inside the JSON-LD itself, so the
    only way to say which ontology a document is, is to compare it against one
    whose release is known. This hashes `@graph` -- and not `@context`, whose
    prefix aliases differ between schema.org and the schemaorg repository for
    one and the same release.
    """
    canonical = json.dumps(_canonical(data["@graph"]), separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

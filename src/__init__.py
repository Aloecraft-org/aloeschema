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

SCHEMA_URL = "https://schema.org/version/latest/schemaorg-current-https.jsonld"


def _is_class_node(node):
    node_types = normalize_to_list(node.get("@type"))
    return "rdfs:Class" in node_types or "schema:DataType" in node_types


def _is_datatype_node(node):
    return "schema:DataType" in normalize_to_list(node.get("@type"))


def _direct_parents(node):
    """Every declared superclass of a class node, not just the first one.

    schema.org is a DAG: 57 types declare more than one rdfs:subClassOf.
    Datatypes additionally hang off the synthetic DataType root.
    """
    parents = [
        p
        for p in (clean_id(p) for p in normalize_to_list(node.get("rdfs:subClassOf")))
        if p
    ]
    name = clean_id(node.get("@id"))
    if _is_datatype_node(node) and name != "DataType" and "DataType" not in parents:
        parents.append("DataType")
    return parents


def _extract_enumeration_values(graph, types):
    enumeration_values = {}
    for node in graph:
        node_type = node.get("@type", "")
        if isinstance(node_type, str):
            node_type = node_type.replace("schema:", "")
        else:
            continue
        if node_type in types and _is_enumeration_type(node_type, types):
            name = node["@id"].replace("schema:", "")
            enumeration_values[name] = {"enum_type": node_type}
    return enumeration_values


def _is_enumeration_type(type_name, types):
    return "Enumeration" in types.get(type_name, {}).get("ancestors", [])


def _transitive_ancestors(name, parents_of, cache, visiting=None):
    """All superclasses of `name`, transitively, including `name` itself.

    Memoised, and guarded against the cycles a hand-edited vocabulary can
    introduce. Names referenced as a parent but never defined as a class node
    (external vocabularies such as fibo: or dcat:) resolve to just themselves.
    """
    if name in cache:
        return cache[name]
    if visiting is None:
        visiting = set()
    if name in visiting:
        return {name}
    visiting.add(name)

    ancestors = {name}
    for parent in parents_of.get(name, ()):
        ancestors |= _transitive_ancestors(parent, parents_of, cache, visiting)

    visiting.discard(name)
    cache[name] = ancestors
    return ancestors


def _extract_types(graph):
    class_nodes = {}
    for node in graph:
        if _is_class_node(node):
            name = clean_id(node.get("@id"))
            if name:
                class_nodes[name] = node

    parents_of = {name: _direct_parents(node) for name, node in class_nodes.items()}

    cache = {}
    for name in class_nodes:
        _transitive_ancestors(name, parents_of, cache)

    def depth(name):
        # Root-first ordering: a type's own ancestor count is its depth.
        return len(cache.get(name, {name}))

    types = {}
    for name in class_nodes:
        ancestors = sorted(cache[name], key=lambda a: (depth(a), a))
        types[name] = {
            "ancestors": ancestors,
            # Retained as an alias of `ancestors` for backwards compatibility.
            # Deprecated: the hierarchy is a DAG, so there is no single path.
            "path": ancestors,
            "properties": [],
            "children": [],
        }

    for name, parents in parents_of.items():
        for parent in parents:
            if parent in types:
                types[parent]["children"].append(name)

    return types


def normalize_to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def clean_id(value):
    if isinstance(value, dict) and "@id" in value:
        return value["@id"].replace("schema:", "")
    elif isinstance(value, str):
        return value.replace("schema:", "")
    return None


def _extract_properties(graph, types):
    properties = {}
    for node in graph:
        if node.get("@type") == "rdf:Property":  # <-- this is the key
            name = node["@id"].replace("schema:", "")
            domains_raw = normalize_to_list(node.get("schema:domainIncludes"))
            ranges_raw = normalize_to_list(node.get("schema:rangeIncludes"))

            domains = [clean_id(d) for d in domains_raw if clean_id(d)]
            ranges = [clean_id(r) for r in ranges_raw if clean_id(r)]

            properties[name] = {
                "domain": domains,
                "range": ranges,
                "datatype": [
                    r
                    for r in ranges
                    if r
                    in (
                        "Text",
                        "URL",
                        "XPathType",
                        "CssSelectorType",
                        "PronounceableText",
                        "Date",
                        "DateTime",
                        "Time",
                        "Number",
                        "Integer",
                        "Float",
                        "Boolean",
                        "False",
                        "True",
                    )
                ],
            }

            # attach property to each domain type
            for d in domains:
                if d in types:
                    types[d]["properties"].append(name)
    return properties


def registerCustomProperty(
    schema_org_dict, name: str, domain: list[str], range: list[str]
) -> dict:
    from aloeschema.error import AloeSchemaError, AloeSchemaErrorType
    from aloeschema.validator import AloeSchemaValidator

    schema_validator = AloeSchemaValidator(schema_org_dict)

    for range_item_type in range:
        # A range entry must be a known type. Value types (Text, Integer, ...)
        # are themselves types, so IsValidType alone is the correct test.
        if not schema_validator.IsValidType(range_item_type):
            raise AloeSchemaError(
                AloeSchemaErrorType.PROPERTY_RANGE_TYPE_NOT_RECOGNIZED,
                f"Range type<{range_item_type}> not a recognized schema.org type or valueType",
            )

    for type in domain:
        schema_validator.Validate(subject_type_name=type)

    schema_org_dict["properties"][name] = {
        "domain": domain,
        "range": range,
        "datatype": [],
    }

    for range_item_type in range:
        if schema_validator.IsValidValueType(range_item_type):
            schema_org_dict["properties"][name]["datatype"].append(range_item_type)

    for parent_type in domain:
        schema_org_dict["types"][parent_type]["properties"].append(name)

    return schema_org_dict


def registerCustomEnumeration(schema_org_dict, name: str) -> dict:
    """Register a new enumeration type (subclass of Enumeration)."""
    return registerCustomType(
        schema_org_dict, name=name, parent="Enumeration", properties=[]
    )


def registerCustomEnumerationValue(schema_org_dict, enum_type: str, value: str) -> dict:
    """Register a new enumeration value (instance of an enumeration type)."""
    from aloeschema.validator import AloeSchemaValidator

    schema_validator = AloeSchemaValidator(schema_org_dict)

    if not schema_validator.IsEnumerationType(enum_type):
        from aloeschema.error import AloeSchemaError, AloeSchemaErrorType

        raise AloeSchemaError(
            AloeSchemaErrorType.ENUMERATION_TYPE_NOT_RECOGNIZED,
            f"Enumeration type<{enum_type}> is not a recognized enumeration type",
        )

    schema_org_dict["enumerations"][value] = {"enum_type": enum_type}
    return schema_org_dict


def registerCustomType(
    schema_org_dict, name: str, parent: str, properties: list[str] = None
) -> dict:
    from aloeschema.validator import AloeSchemaValidator

    properties = list(properties) if properties else []

    schema_validator = AloeSchemaValidator(schema_org_dict)
    schema_validator.Validate(subject_type_name=parent)
    for prop in properties:
        schema_validator.Validate(property_type_name=prop)

    parent_entry = schema_org_dict["types"][parent]
    parent_entry.setdefault("children", []).append(name)

    # Copy the parent's ancestors. Aliasing the parent's list here and
    # appending to it rewrites the parent's own ancestry in place, which made
    # every sibling an ancestor of every other sibling.
    ancestors = list(parent_entry.get("ancestors", parent_entry.get("path", []))) + [
        name
    ]

    schema_org_dict["types"][name] = {
        "ancestors": ancestors,
        "path": ancestors,
        # Only properties declared directly on this type. Properties inherited
        # from ancestors are resolved during validation by walking `ancestors`,
        # so materialising them here would just duplicate that.
        "properties": properties,
        "children": [],
    }
    for prop in properties:
        schema_org_dict["properties"][prop]["domain"].append(name)

    return schema_org_dict


def load_schema_org(fetch=False):
    data = {}
    if fetch:
        try:
            import requests
        except ImportError as exc:
            raise ImportError(
                "load_schema_org(fetch=True) needs the 'requests' package. "
                "Install it with: pip install aloeschema[fetch]"
            ) from exc

        data = requests.get(SCHEMA_URL).json()
    else:
        from aloeschema.data.schemaorg_current import schemaorg_current_jsonld

        data = schemaorg_current_jsonld

    schema_graph = data["@graph"]
    schema_types = _extract_types(schema_graph)
    schema_properties = _extract_properties(schema_graph, schema_types)
    schema_enumerations = _extract_enumeration_values(schema_graph, schema_types)
    return {
        "graph": schema_graph,
        "types": schema_types,
        "properties": schema_properties,
        "enumerations": schema_enumerations,
    }


if __name__ == "__main__":
    schema_org = load_schema_org()

    # `ancestors` holds every transitive superclass, including the type itself.
    # `path` is a deprecated alias of `ancestors`, kept for backwards
    # compatibility; the hierarchy is a DAG, so there is no single path.

    schema_org["types"]["DataType"]
    # {'ancestors': ['rdfs:Class', 'DataType'], 'path': [...], 'properties': [], 'children': ['DateTime', 'Date', 'Boolean', 'Time', 'Text', 'Number']}

    schema_org["properties"]["knowsAbout"]
    # {'domain': ['Person', 'Organization'], 'range': ['Text', 'Thing', 'URL'], 'datatype': ['Text', 'URL']}

    schema_org["types"]["MoveAction"]
    # {'ancestors': ['Thing', 'Action', 'MoveAction'], 'path': [...], 'properties': ['fromLocation', 'toLocation'], 'children': ['ArriveAction', 'TravelAction', 'DepartAction']}

    schema_org["types"]["Number"]
    # {'ancestors': ['rdfs:Class', 'DataType', 'Number'], 'path': [...], 'properties': [], 'children': ['Integer', 'Float']}

    # Multiple inheritance is preserved: Diet is both a CreativeWork and a
    # LifestyleModification, and reaches Thing through the former.
    schema_org["types"]["Diet"]
    # {'ancestors': ['Thing', 'CreativeWork', 'MedicalEntity', 'LifestyleModification', 'Diet'], ...}

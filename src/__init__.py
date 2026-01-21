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

import requests

SCHEMA_URL = "https://schema.org/version/latest/schemaorg-current-https.jsonld"

def _add_children(graph, types):
    for node in graph:
        if node.get("@type") == "rdfs:Class" or "schema:DataType" in node.get("@type"):
            name = node["@id"].replace("schema:", "")
            parents = normalize_to_list(node.get("rdfs:subClassOf"))
            
            # normal parent linking
            for parent in parents:
                parent_id = clean_id(parent)
                if parent_id and parent_id in types:
                    types[parent_id].setdefault("children", []).append(name)

            # special case: datatypes should be children of DataType
            if "schema:DataType" in node.get("@type"):
                if "DataType" in types:
                    types["DataType"].setdefault("children", []).append(name)    

def _extract_types(graph):
    types = {}
    for node in graph:
        if node.get("@type") == "rdfs:Class" or "schema:DataType" in node.get("@type"):
            name = node["@id"].replace("schema:", "")
            path = [name]

            # special case: if it's a schema:DataType, add DataType at the front
            if "schema:DataType" in node.get("@type"):
                path.insert(0, "DataType")
            
            # normalize to list
            parents = node.get("rdfs:subClassOf")
            if parents and not isinstance(parents, list):
                parents = [parents]

            while parents:
                # just take the first parent for path (schema.org often has multiple)
                parent = parents[0]
                parent_id = parent["@id"].replace("schema:", "")
                path.insert(0, parent_id)

                # find parent node
                parent_node = next((n for n in graph if n["@id"] == parent["@id"]), None)
                if parent_node:
                    # if the parent itself is a schema:DataType, ensure DataType is at the root
                    if "schema:DataType" in parent_node.get("@type", []):
                        if path[0] != "DataType":
                            path.insert(0, "DataType")
                            
                    next_parents = parent_node.get("rdfs:subClassOf")
                    if next_parents and not isinstance(next_parents, list):
                        next_parents = [next_parents]
                    parents = next_parents
                else:
                    parents = None

            # ensure DataType is at the root if this node or any ancestor is a schema:DataType
            if "schema:DataType" in node.get("@type") or "DataType" in path:
                if path[0] != "DataType":
                    path.insert(0, "DataType")                    

            types[name] = {"path": path, "properties": []}
    _add_children(graph, types)
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
        if node.get("@type") == "rdf:Property":   # <-- this is the key
            name = node["@id"].replace("schema:", "")
            domains_raw = normalize_to_list(node.get("schema:domainIncludes"))
            ranges_raw = normalize_to_list(node.get("schema:rangeIncludes"))

            domains = [clean_id(d) for d in domains_raw if clean_id(d)]
            ranges = [clean_id(r) for r in ranges_raw if clean_id(r)]

            properties[name] = {
                "domain": domains,
                "range": ranges,
                "datatype": [r for r in ranges if r in (
                    "Text","URL","XPathType","CssSelectorType","PronounceableText",
                    "Date","DateTime","Time","Number","Integer","Float","Boolean","False","True"
                )]
            }

            # attach property to each domain type
            for d in domains:
                if d in types:
                    types[d]["properties"].append(name)
    return properties

def registerCustomProperty(schema_org_dict, name:str, domain:list[str], range:list[str]) -> dict:
    from aloeschema.error import AloeSchemaError, AloeSchemaErrorType
    from aloeschema.validator import AloeSchemaValidator
    
    schema_validator = AloeSchemaValidator(schema_org_dict)

    for range_item_type in range:
        if not schema_validator.IsValidType(range_item_type) or schema_validator.IsValidValueType(range_item_type):
            raise AloeSchemaError(AloeSchemaErrorType.PROPERTY_RANGE_TYPE_NOT_RECOGNIZED, f"Range type<{range_item_type}> not a recognized schema.org type or valueType")
    
    for type in domain:
        schema_validator.Validate(subject_type_name=type)

    schema_org_dict["properties"][name] = {'domain': domain, 'range': range, 'datatype': []}

    for range_item_type in range:
        if schema_validator.IsValidValueType(range_item_type):
            schema_org_dict["properties"][name]['datatype'].append(range_item_type)
            
    for parent_type in domain:
        schema_org_dict["types"][parent_type]['properties'].append(name)
        
    return schema_org_dict

def registerCustomType(schema_org_dict, name:str, parent:str, properties:list[str]=[]) -> dict:
    from aloeschema.validator import AloeSchemaValidator
    schema_validator = AloeSchemaValidator(schema_org_dict)
    schema_validator.Validate(subject_type_name=parent)
    for prop in properties:
        schema_validator.Validate(property_type_name=prop)
        
    schema_org_dict["types"][parent]['children'].append(name)
    path = schema_org_dict["types"][parent]['path']
    path.append(name)

    schema_org_dict["types"][name] = {'path':path, 'properties':properties, 'children': []}
    for prop in schema_org_dict["types"][parent]['properties']:
        schema_org_dict["types"][name]['properties'].append(prop)
        schema_org_dict["properties"][prop]['domain'].append(name)
        
    return schema_org_dict

def load_schema_org(fetch=False):
    data = {}
    if fetch:
        data = requests.get(SCHEMA_URL).json()
    else:
        from aloeschema.data.schemaorg_current import schemaorg_current_jsonld
        data = schemaorg_current_jsonld

    schema_graph = data["@graph"]
    schema_types = _extract_types(schema_graph)
    schema_properties = _extract_properties(schema_graph, schema_types)
    return {
        "graph": schema_graph,
        "types": schema_types,
        "properties": schema_properties
    }

if __name__ == "__main__":
    
    schema_org = load_schema_org()
    
    schema_org['types']["DataType"]
    # {'path': ['rdfs:Class', 'DataType'], 'properties': [], 'children': ['DateTime', 'Date', 'Boolean', 'Time', 'Text', 'Number']}
    
    schema_org['properties']['knowsAbout']
    # {'domain': ['Person', 'Organization'], 'range': ['Text', 'Thing', 'URL'], 'datatype': ['Text', 'URL']}
    
    schema_org['types']['MoveAction']
    # {'path': ['Thing', 'Action', 'MoveAction'], 'properties': ['fromLocation', 'toLocation'], 'children': ['ArriveAction', 'TravelAction', 'DepartAction']}

    schema_org['types']['Number']
    # {'path': ['DataType', 'Number'], 'properties': [], 'children': ['Integer', 'Float']}
    
    schema_org['types']['Integer']
    # {'path': ['DataType', 'Number', 'Integer'], 'properties': []}
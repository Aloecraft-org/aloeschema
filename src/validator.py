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
from aloeschema.constant import AloeSchemaErrorType
from aloeschema.error import AloeSchemaError

class AloeSchemaValidator:

    def __init__(self, schema_org):
        self.schema_org = schema_org

    def _getType(self, type_name:str, ignore_case=True):
        if ignore_case:
            type_list = [v for k,v in self.schema_org["types"].items() if k.lower() == type_name.lower()]
            if type_list:
                return type_list[0]
            else:
                return None
        else:
            return self.schema_org["types"].get(type_name, None)

    def _getProperty(self, property_name:str, ignore_case=True):
        if ignore_case:
            property_list = [v for k,v in self.schema_org["properties"].items() if k.lower() == property_name.lower()]
            if property_list:
                return property_list[0]
            else:
                return None
        else:
            return self.schema_org["properties"].get(property_name, None)

    def _item_in(self, item, collection, ignore_case=True):
        return (item.lower() if ignore_case else item) in [c.lower() if ignore_case else c for c in collection]
    
    def IsValidType(self, type_name:str, ignore_case=True) -> bool:
        return self._getType(type_name, ignore_case)

    def IsValidPropertyType(self, property_type_name:str, ignore_case=True) -> bool:
        return self._getProperty(property_type_name, ignore_case)

    def IsValidValueType(self, value_type_name:str, ignore_case=True) -> bool:
        return self.IsValidType(value_type_name, ignore_case) and 'DataType' in self._getType(value_type_name, ignore_case).get('path', [])

    def TypeDescendantOf(self, parent_type_name:str, child_type_name:str, ignore_case=True, quiet=False) -> bool:
        if not self.IsValidType(parent_type_name,ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Parent type<{parent_type_name}> not a recognized schema.org type")

        if not self.IsValidType(child_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Child type<{child_type_name}> not a recognized schema.org type")

        return self._item_in(parent_type_name,self._getType(child_type_name, ignore_case).get('path', []),ignore_case)            
    
    def TypeInPropertyRange(self, property_type_name:str, object_type_name:str, ignore_case=True, quiet=False) -> bool:
        if not self.IsValidType(object_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Object type<{object_type_name}> not a recognized schema.org type")
        if not self.IsValidPropertyType(property_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.PROPERTY_TYPE_NOT_RECOGNIZED, f"Property<{property_type_name}> not a recognized schema.org property type")

        return any([self._item_in(ancestor, self._getProperty(property_type_name, ignore_case).get('range', []),ignore_case) for ancestor in self._getType(object_type_name, ignore_case)["path"]])            

    def TypeInPropertyDomain(self, subject_type_name:str, property_type_name:str, ignore_case=True, quiet=False) -> bool:
        if not self.IsValidType(subject_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Subject type<{subject_type_name}> not a recognized schema.org type")
        if not self.IsValidPropertyType(property_type_name,ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.PROPERTY_TYPE_NOT_RECOGNIZED, f"Property<{property_type_name}> not a recognized schema.org property type")

        return any([self._item_in(ancestor, self._getProperty(property_type_name, ignore_case).get('domain', []),ignore_case) for ancestor in self._getType(subject_type_name, ignore_case)["path"]])
        
    def ValueTypeInProperty(self, property_type_name:str, value_type_name:str, ignore_case=True, quiet=False) -> bool:
        if not self.IsValidValueType(value_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.VALUE_TYPE_NOT_RECOGNIZED, f"Value type<{value_type_name}> not a recognized schema.org value type")
        if not self.IsValidPropertyType(property_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.PROPERTY_TYPE_NOT_RECOGNIZED, f"Property<{property_type_name}> not a recognized schema.org property type")
        return self._item_in(value_type_name,self._getProperty(property_type_name, ignore_case).get('datatype', []),ignore_case)            
    
    def Validate(self, subject_type_name:str = None, property_type_name:str = None, object_type_name:str = None,  value_type_name:str=None, ignore_case=True, quiet=False) -> bool:
        if subject_type_name and not self.IsValidType(subject_type_name, ignore_case):
            if quiet:
                return False
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Subject type<{subject_type_name}> not a recognized schema.org type")
        if property_type_name and not self.IsValidPropertyType(property_type_name, ignore_case):
            if quiet:
                return False            
            raise AloeSchemaError(AloeSchemaErrorType.PROPERTY_TYPE_NOT_RECOGNIZED, f"Property<{property_type_name}> not a recognized schema.org property type")
        if object_type_name and not self.IsValidType(object_type_name, ignore_case):
            if quiet:
                return False            
            raise AloeSchemaError(AloeSchemaErrorType.TYPE_NOT_RECOGNIZED, f"Object type<{object_type_name}> not a recognized schema.org type")
        if value_type_name and not self.IsValidValueType(value_type_name, ignore_case):
            if quiet:
                return False            
            raise AloeSchemaError(AloeSchemaErrorType.VALUE_TYPE_NOT_RECOGNIZED, f"Value type<{value_type_name}> not a recognized schema.org value type")
        if subject_type_name and property_type_name:
            if not self.TypeInPropertyDomain(subject_type_name, property_type_name, ignore_case, quiet):
                return False
        if property_type_name and object_type_name:
            if not self.TypeInPropertyRange(property_type_name, object_type_name, ignore_case, quiet):
                return False
        if property_type_name and value_type_name:
            if not self.ValueTypeInProperty(property_type_name, value_type_name, ignore_case, quiet):
                return False        
        return True

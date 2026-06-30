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

from aloeschema.error import AloeSchemaErrorType, AloeSchemaError
from aloeschema.validator import AloeSchemaValidator
from aloeschema import load_schema_org

aloe_schema_org = load_schema_org()
schema_validator =  AloeSchemaValidator(aloe_schema_org)

import unittest

class TestFuncs(unittest.TestCase):
    def test_invalidSubjectTypeName_raisesAloeSchemaError(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(subject_type_name="This")

    def test_invalidObjectTypeName_raisesAloeSchemaError(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(object_type_name="Sh*t")

    def test_invalidPropertyTypeName_raisesAloeSchemaError(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(property_type_name="Is")

    def test_invalidValueTypeName_raisesAloeSchemaError(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(value_type_name="Bananas")

    def test_typeTests_ReturnFalse(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        self.assertFalse(schema_validator.IsValidValueType(value_type_name="B-a-n-a-n-a-s"))
        self.assertFalse(schema_validator.IsValidPropertyType(property_type_name="B-a-n-a-n-a-s"))
        self.assertFalse(schema_validator.IsValidType(type_name="B-a-n-a-n-a-s"))

    def test_typeTests_ReturnTrue(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        self.assertTrue(schema_validator.IsValidValueType(value_type_name="Integer"))
        self.assertTrue(schema_validator.IsValidPropertyType(property_type_name="knowsAbout"))
        self.assertTrue(schema_validator.IsValidType(type_name="Person"))

    def test_Validate(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        
        self.assertTrue(schema_validator.Validate(subject_type_name="Person"))
        self.assertTrue(schema_validator.Validate(subject_type_name="person", ignore_case=True))
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(subject_type_name="Personzz")
            schema_validator.Validate(subject_type_name="pErSon", ignore_case=False)

        self.assertTrue(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsAbout"))        
        with self.assertRaises(AloeSchemaError):
            self.assertTrue(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsStuff"))
        
        self.assertTrue(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsAbout", object_type_name="Thing"))
        with self.assertRaises(AloeSchemaError):
            self.assertTrue(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsAbout", object_type_name="Secret Sauce"))
            
        self.assertTrue(schema_validator.TypeDescendantOf("Thing", "Person"))
        self.assertFalse(schema_validator.TypeDescendantOf("Person", "Thing"))

    def test_inheritsAncestorProperties(self):
        schema_validator.Validate(subject_type_name="person", property_type_name="potentialAction", object_type_name="planAction", quiet=False)

    def test_enumerations(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        from aloeschema import registerCustomEnumeration, registerCustomEnumerationValue

        # IsEnumerationType
        self.assertTrue(schema_validator.IsEnumerationType("DayOfWeek"))
        self.assertFalse(schema_validator.IsEnumerationType("Person"))
        self.assertFalse(schema_validator.IsEnumerationType("B-a-n-a-n-a-s"))

        # Built-in enum values extracted from schema.org
        self.assertTrue(schema_validator.IsValidEnumerationValue("Monday"))
        self.assertFalse(schema_validator.IsValidEnumerationValue("Mondayyyy"))

        # EnumerationValueIsOfType
        self.assertTrue(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        self.assertFalse(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday", quiet=True) == False
                         or not schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Mondayyyy")
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("B-a-n-a-n-a-s", "Monday")

        # Custom enum registration
        custom_schema = registerCustomEnumeration(aloe_schema_org.copy(), name="TaskStatus")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Active")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Pending")
        custom_validator = AloeSchemaValidator(custom_schema)

        self.assertTrue(custom_validator.IsEnumerationType("TaskStatus"))
        self.assertTrue(custom_validator.IsValidEnumerationValue("Active"))
        self.assertTrue(custom_validator.EnumerationValueIsOfType("TaskStatus", "Active"))
        self.assertFalse(custom_validator.EnumerationValueIsOfType("TaskStatus", "Monday", quiet=True))

    def test_enumerations(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        from aloeschema import registerCustomEnumeration, registerCustomEnumerationValue

        # IsEnumerationType
        self.assertTrue(schema_validator.IsEnumerationType("DayOfWeek"))
        self.assertFalse(schema_validator.IsEnumerationType("Person"))
        self.assertFalse(schema_validator.IsEnumerationType("B-a-n-a-n-a-s"))

        # Built-in enum values extracted from schema.org
        self.assertTrue(schema_validator.IsValidEnumerationValue("Monday"))
        self.assertFalse(schema_validator.IsValidEnumerationValue("Mondayyyy"))

        # EnumerationValueIsOfType
        self.assertTrue(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        self.assertFalse(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday", quiet=True) == False
                         or not schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Mondayyyy")
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("B-a-n-a-n-a-s", "Monday")

        # Custom enum registration
        custom_schema = registerCustomEnumeration(aloe_schema_org.copy(), name="TaskStatus")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Active")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Pending")
        custom_validator = AloeSchemaValidator(custom_schema)

        self.assertTrue(custom_validator.IsEnumerationType("TaskStatus"))
        self.assertTrue(custom_validator.IsValidEnumerationValue("Active"))
        self.assertTrue(custom_validator.EnumerationValueIsOfType("TaskStatus", "Active"))
        self.assertFalse(custom_validator.EnumerationValueIsOfType("TaskStatus", "Monday", quiet=True))

    def test_enumerations(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)
        from aloeschema import registerCustomEnumeration, registerCustomEnumerationValue

        # IsEnumerationType
        self.assertTrue(schema_validator.IsEnumerationType("DayOfWeek"))
        self.assertFalse(schema_validator.IsEnumerationType("Person"))
        self.assertFalse(schema_validator.IsEnumerationType("B-a-n-a-n-a-s"))

        # Built-in enum values extracted from schema.org
        self.assertTrue(schema_validator.IsValidEnumerationValue("Monday"))
        self.assertFalse(schema_validator.IsValidEnumerationValue("Mondayyyy"))

        # EnumerationValueIsOfType
        self.assertTrue(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        self.assertFalse(schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday", quiet=True) == False
                         or not schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday"))
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Mondayyyy")
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("B-a-n-a-n-a-s", "Monday")

        # Custom enum registration
        custom_schema = registerCustomEnumeration(aloe_schema_org.copy(), name="TaskStatus")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Active")
        custom_schema = registerCustomEnumerationValue(custom_schema, enum_type="TaskStatus", value="Pending")
        custom_validator = AloeSchemaValidator(custom_schema)

        self.assertTrue(custom_validator.IsEnumerationType("TaskStatus"))
        self.assertTrue(custom_validator.IsValidEnumerationValue("Active"))
        self.assertTrue(custom_validator.EnumerationValueIsOfType("TaskStatus", "Active"))
        self.assertFalse(custom_validator.EnumerationValueIsOfType("TaskStatus", "Monday", quiet=True))

    def test_ValidateQuiet(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)

        self.assertFalse(schema_validator.Validate(subject_type_name="Personzz", quiet=True))
        self.assertFalse(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsStuff", quiet=True))
        self.assertFalse(schema_validator.Validate(subject_type_name="Person", property_type_name="knowsAbout", object_type_name="Secret Sauce", quiet=True))

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestFuncs))
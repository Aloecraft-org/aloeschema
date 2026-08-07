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

import unittest
from copy import deepcopy

from aloeschema import (
    load_schema_org,
    registerCustomProperty,
    registerCustomType,
)
from aloeschema.error import AloeSchemaError
from aloeschema.validator import AloeSchemaValidator

aloe_schema_org = load_schema_org()
schema_validator = AloeSchemaValidator(aloe_schema_org)


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

        self.assertFalse(
            schema_validator.IsValidValueType(value_type_name="B-a-n-a-n-a-s")
        )
        self.assertFalse(
            schema_validator.IsValidPropertyType(property_type_name="B-a-n-a-n-a-s")
        )
        self.assertFalse(schema_validator.IsValidType(type_name="B-a-n-a-n-a-s"))

    def test_typeTests_ReturnTrue(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)

        self.assertTrue(schema_validator.IsValidValueType(value_type_name="Integer"))
        self.assertTrue(
            schema_validator.IsValidPropertyType(property_type_name="knowsAbout")
        )
        self.assertTrue(schema_validator.IsValidType(type_name="Person"))

    def test_Validate(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)

        self.assertTrue(schema_validator.Validate(subject_type_name="Person"))
        self.assertTrue(
            schema_validator.Validate(subject_type_name="person", ignore_case=True)
        )
        with self.assertRaises(AloeSchemaError):
            schema_validator.Validate(subject_type_name="Personzz")
            schema_validator.Validate(subject_type_name="pErSon", ignore_case=False)

        self.assertTrue(
            schema_validator.Validate(
                subject_type_name="Person", property_type_name="knowsAbout"
            )
        )
        with self.assertRaises(AloeSchemaError):
            self.assertTrue(
                schema_validator.Validate(
                    subject_type_name="Person", property_type_name="knowsStuff"
                )
            )

        self.assertTrue(
            schema_validator.Validate(
                subject_type_name="Person",
                property_type_name="knowsAbout",
                object_type_name="Thing",
            )
        )
        with self.assertRaises(AloeSchemaError):
            self.assertTrue(
                schema_validator.Validate(
                    subject_type_name="Person",
                    property_type_name="knowsAbout",
                    object_type_name="Secret Sauce",
                )
            )

        self.assertTrue(schema_validator.TypeDescendantOf("Thing", "Person"))
        self.assertFalse(schema_validator.TypeDescendantOf("Person", "Thing"))

    def test_inheritsAncestorProperties(self):
        # potentialAction is declared on Thing, so Person must inherit it.
        self.assertTrue(
            schema_validator.Validate(
                subject_type_name="person",
                property_type_name="potentialAction",
                object_type_name="planAction",
                quiet=False,
            )
        )

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
        self.assertTrue(
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday")
        )
        self.assertTrue(
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Monday", quiet=True)
        )
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("DayOfWeek", "Mondayyyy")
        with self.assertRaises(AloeSchemaError):
            schema_validator.EnumerationValueIsOfType("B-a-n-a-n-a-s", "Monday")

        # Custom enum registration. deepcopy because the register* helpers mutate
        # the schema they are given, and a shallow copy shares the nested dicts.
        custom_schema = registerCustomEnumeration(
            deepcopy(aloe_schema_org), name="TaskStatus"
        )
        custom_schema = registerCustomEnumerationValue(
            custom_schema, enum_type="TaskStatus", value="Active"
        )
        custom_schema = registerCustomEnumerationValue(
            custom_schema, enum_type="TaskStatus", value="Pending"
        )
        custom_validator = AloeSchemaValidator(custom_schema)

        self.assertTrue(custom_validator.IsEnumerationType("TaskStatus"))
        self.assertTrue(custom_validator.IsValidEnumerationValue("Active"))
        self.assertTrue(
            custom_validator.EnumerationValueIsOfType("TaskStatus", "Active")
        )
        self.assertFalse(
            custom_validator.EnumerationValueIsOfType(
                "TaskStatus", "Monday", quiet=True
            )
        )

    def test_ValidateQuiet(self):
        schema_validator = AloeSchemaValidator(aloe_schema_org)

        self.assertFalse(
            schema_validator.Validate(subject_type_name="Personzz", quiet=True)
        )
        self.assertFalse(
            schema_validator.Validate(
                subject_type_name="Person", property_type_name="knowsStuff", quiet=True
            )
        )
        self.assertFalse(
            schema_validator.Validate(
                subject_type_name="Person",
                property_type_name="knowsAbout",
                object_type_name="Secret Sauce",
                quiet=True,
            )
        )


class TestRegressions(unittest.TestCase):
    """One test per defect fixed in stage 1 of the roadmap."""

    def setUp(self):
        self.schema = deepcopy(aloe_schema_org)

    def test_registerCustomType_doesNotMutateParentAncestry(self):
        before = list(self.schema["types"]["Person"]["ancestors"])
        schema = registerCustomType(self.schema, name="User", parent="Person")
        schema = registerCustomType(schema, name="Admin", parent="Person")

        self.assertEqual(schema["types"]["Person"]["ancestors"], before)
        self.assertEqual(schema["types"]["User"]["ancestors"], before + ["User"])
        self.assertEqual(schema["types"]["Admin"]["ancestors"], before + ["Admin"])

        validator = AloeSchemaValidator(schema)
        # The parent is not a descendant of its own child, and siblings are
        # unrelated to each other.
        self.assertFalse(validator.TypeDescendantOf("User", "Person"))
        self.assertTrue(validator.TypeDescendantOf("Person", "User"))
        self.assertFalse(validator.TypeDescendantOf("User", "Admin"))

    def test_registerCustomType_underLeafParent(self):
        # Leaf types had no "children" key, so registering under one raised
        # KeyError.
        schema = registerCustomType(
            self.schema, name="NightLocksmith", parent="Locksmith"
        )
        self.assertIn("NightLocksmith", schema["types"]["Locksmith"]["children"])
        self.assertIn("Locksmith", schema["types"]["NightLocksmith"]["ancestors"])

    def test_registerCustomType_hasNoMutableDefault(self):
        self.assertNotIn([], registerCustomType.__defaults__ or ())

    def test_registerCustomProperty_acceptsDataTypeRange(self):
        # The range guard was inverted, so every value type was rejected.
        schema = registerCustomType(self.schema, name="User", parent="Person")
        schema = registerCustomProperty(
            schema, name="userName", domain=["Person", "User"], range=["Text"]
        )
        self.assertEqual(schema["properties"]["userName"]["datatype"], ["Text"])
        self.assertTrue(
            AloeSchemaValidator(schema).Validate(
                subject_type_name="User",
                property_type_name="userName",
                value_type_name="Text",
            )
        )

    def test_customType_inheritsAncestorProperties(self):
        schema = registerCustomType(self.schema, name="User", parent="Person")
        self.assertTrue(
            AloeSchemaValidator(schema).Validate(
                subject_type_name="User",
                property_type_name="knowsAbout",
                object_type_name="Thing",
            )
        )

    def test_multipleInheritanceIsPreserved(self):
        validator = AloeSchemaValidator(self.schema)

        # Diet declares both CreativeWork and LifestyleModification as parents.
        self.assertTrue(validator.TypeDescendantOf("CreativeWork", "Diet"))
        self.assertTrue(validator.TypeDescendantOf("LifestyleModification", "Diet"))
        self.assertTrue(
            validator.Validate(subject_type_name="Diet", property_type_name="author")
        )

        # TVSeason likewise.
        self.assertTrue(validator.TypeDescendantOf("CreativeWork", "TVSeason"))
        self.assertTrue(validator.TypeDescendantOf("CreativeWorkSeason", "TVSeason"))

    def test_everySchemaOrgTypeReachesThingOrDataType(self):
        # Following only the first parent detached 84 types from the hierarchy.
        # Terms carrying an external prefix (dcat:, fibo:, ...) are roots of
        # other vocabularies and legitimately have no schema.org ancestor.
        orphans = [
            name
            for name, entry in self.schema["types"].items()
            if ":" not in name
            and "Thing" not in entry["ancestors"]
            and "DataType" not in entry["ancestors"]
        ]
        self.assertEqual(orphans, [])

    def test_errorIsCaughtByExceptHandler(self):
        # AloeSchemaError extended BaseException, so it slipped past
        # `except Exception:` in calling code.
        self.assertTrue(issubclass(AloeSchemaError, Exception))
        with self.assertRaises(Exception):
            AloeSchemaValidator(self.schema).Validate(subject_type_name="Nope")

    def test_validityChecksReturnBooleans(self):
        validator = AloeSchemaValidator(self.schema)
        for value in (
            validator.IsValidType("Person"),
            validator.IsValidType("B-a-n-a-n-a-s"),
            validator.IsValidPropertyType("knowsAbout"),
            validator.IsValidValueType("Integer"),
        ):
            self.assertIsInstance(value, bool)

    def test_pathIsAnAliasOfAncestors(self):
        entry = self.schema["types"]["MoveAction"]
        self.assertEqual(entry["path"], entry["ancestors"])
        self.assertEqual(entry["ancestors"], ["Thing", "Action", "MoveAction"])


if __name__ == "__main__":
    unittest.main()

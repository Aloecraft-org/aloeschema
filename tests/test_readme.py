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
"""The examples in README.md, executed.

Both bugs fixed in 0.3.2 and 0.3.3 were in this path and neither was caught:
the package shipped without its ontology, so the first example raised
ModuleNotFoundError on any pip install, and `registerCustomProperty` rejected
every datatype range, so the extension example raised on `range=["Text"]`.
The suite covered the library but not the thing the README tells people to
run, so that is what this covers.
"""

import unittest

from aloeschema import (
    load_schema_org,
    registerCustomEnumeration,
    registerCustomEnumerationValue,
    registerCustomProperty,
    registerCustomType,
)
from aloeschema.error import AloeSchemaError
from aloeschema.validator import AloeSchemaValidator


class TestReadmeExamples(unittest.TestCase):
    def setUp(self):
        self.schema_org = load_schema_org()

    def test_initializationAndValidation(self):
        v = AloeSchemaValidator(self.schema_org)
        self.assertTrue(
            v.Validate(
                subject_type_name="person",
                property_type_name="potentialaction",
                object_type_name="planaction",
            )
        )
        self.assertTrue(v._getType("schedule"))

    def test_extendingWithCustomTypesPropertiesAndEnumerations(self):
        s = registerCustomType(
            self.schema_org, name="User", parent="Person", properties=[]
        )
        s = registerCustomProperty(
            s, name="userName", domain=["Person", "User"], range=["Text"]
        )
        s = registerCustomEnumeration(s, name="TaskStatus")
        s = registerCustomEnumerationValue(
            s, enum_type="TaskStatus", value="TaskStatusActive"
        )
        s = registerCustomProperty(
            s, name="taskStatus", domain=["User"], range=["TaskStatus"]
        )
        v = AloeSchemaValidator(s)

        self.assertTrue(v.IsEnumerationType("TaskStatus"))
        self.assertTrue(v.EnumerationValueIsOfType("TaskStatus", "TaskStatusActive"))
        self.assertTrue(
            v.Validate(
                subject_type_name="User",
                property_type_name="taskStatus",
                enumeration_value_name="TaskStatusActive",
            )
        )


class TestCustomPropertyRange(unittest.TestCase):
    """The guard rejected exactly the datatypes it was meant to accept:
    IsValidValueType is a subset of IsValidType, so `Text` satisfied the
    second arm of an `or` and raised."""

    def setUp(self):
        self.schema_org = load_schema_org()

    def test_datatypeRangesAreAccepted(self):
        for datatype in ("Text", "Number", "Boolean", "Date", "DateTime"):
            with self.subTest(range=datatype):
                s = registerCustomProperty(
                    load_schema_org(),
                    name="probe",
                    domain=["Person"],
                    range=[datatype],
                )
                self.assertEqual(s["properties"]["probe"]["range"], [datatype])
                self.assertEqual(s["properties"]["probe"]["datatype"], [datatype])

    def test_classRangesAreAccepted(self):
        s = registerCustomProperty(
            self.schema_org, name="probe", domain=["Person"], range=["Organization"]
        )
        self.assertEqual(s["properties"]["probe"]["range"], ["Organization"])
        self.assertEqual(s["properties"]["probe"]["datatype"], [])

    def test_anUnknownRangeStillRaises(self):
        with self.assertRaises(AloeSchemaError):
            registerCustomProperty(
                self.schema_org,
                name="probe",
                domain=["Person"],
                range=["NotASchemaOrgType"],
            )


if __name__ == "__main__":
    unittest.main()

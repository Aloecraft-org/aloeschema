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
"""The README's examples, executed.

This module deliberately imports nothing from the source tree beyond the
public package, so CI can run it against an installed wheel to prove the
published artifact works. The packaged distribution once omitted
aloeschema.data entirely, which made the first example in the README raise
ModuleNotFoundError for every user who installed from PyPI.
"""

import unittest

from aloeschema import (
    load_schema_org,
    registerCustomEnumeration,
    registerCustomEnumerationValue,
    registerCustomProperty,
    registerCustomType,
)
from aloeschema.validator import AloeSchemaValidator


class TestReadmeExamples(unittest.TestCase):
    def test_initialization(self):
        schema_org = load_schema_org()
        AloeSchemaValidator(schema_org)

        self.assertIn("types", schema_org)
        self.assertIn("properties", schema_org)
        self.assertIn("enumerations", schema_org)
        self.assertGreater(len(schema_org["types"]), 900)
        self.assertGreater(len(schema_org["properties"]), 1500)

    def test_validating_schema_org(self):
        schema_validator = AloeSchemaValidator(load_schema_org())

        self.assertTrue(
            schema_validator.Validate(
                subject_type_name="person",
                property_type_name="potentialaction",
                object_type_name="planaction",
            )
        )
        self.assertIsNotNone(schema_validator._getType("schedule"))

    def test_extending_with_custom_types_properties_and_enumerations(self):
        schema_org = load_schema_org()

        schema_org = registerCustomType(
            schema_org, name="User", parent="Person", properties=[]
        )
        schema_org = registerCustomProperty(
            schema_org, name="userName", domain=["Person", "User"], range=["Text"]
        )

        schema_org = registerCustomEnumeration(schema_org, name="TaskStatus")
        schema_org = registerCustomEnumerationValue(
            schema_org, enum_type="TaskStatus", value="TaskStatusActive"
        )
        schema_org = registerCustomProperty(
            schema_org, name="taskStatus", domain=["User"], range=["TaskStatus"]
        )

        schema_validator = AloeSchemaValidator(schema_org)

        self.assertTrue(schema_validator.IsEnumerationType("TaskStatus"))
        self.assertTrue(
            schema_validator.EnumerationValueIsOfType("TaskStatus", "TaskStatusActive")
        )
        self.assertTrue(
            schema_validator.Validate(
                subject_type_name="User",
                property_type_name="taskStatus",
                enumeration_value_name="TaskStatusActive",
            )
        )

    def test_fetchIsOptionalAndDoesNotBreakTheDefaultPath(self):
        # requests is an extra, not a hard dependency. The bundled snapshot
        # must load without it.
        import sys

        self.assertNotIn("requests", sys.modules.get("aloeschema", sys).__dict__)
        self.assertGreater(len(load_schema_org()["types"]), 900)


if __name__ == "__main__":
    unittest.main()

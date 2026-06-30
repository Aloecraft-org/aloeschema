# AloeSchema

<div align="center">

<img src="doc/icon.png" style="height:96px; width:96px;"/>

**A Schema.org Multitool**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Repo](https://img.shields.io/badge/github-repo-blue.svg)](https://github.com/Aloecraft-org/AloeSchema)


</div>

## Getting Started

See **quickstart.ipynb** for more detailed usage examples

**Installation**:
```sh
pip install aloeschema
```

**Initialization**: Loads schema.org and a validator

``` py
from aloeschema import load_schema_org
from aloeschema.validator import AloeSchemaValidator
schema_org = load_schema_org()
schema_validator =  AloeSchemaValidator(schema_org)
```

**Validating schema.org**
- Input case is ignored by default (`ignore_case=True`)
- Detailed errors raised by default (`quiet=False`)
    + Set `quiet=True` to return a truthy result instead

``` py
from aloeschema.validator import AloeSchemaValidator
from aloeschema import load_schema_org

schema_org = load_schema_org()
schema_validator = AloeSchemaValidator(schema_org)

schema_validator.Validate(subject_type_name="person", property_type_name="potentialaction", object_type_name="planaction")
schema_validator._getType("schedule")
```

**Extending Schema.org With Custom Types, Properties, and Enumerations**

use `registerCustomType`, `registerCustomProperty`, `registerCustomEnumeration`, and `registerCustomEnumerationValue` to extend Schema.org

``` py
from aloeschema.validator import AloeSchemaValidator
from aloeschema import load_schema_org, registerCustomProperty, registerCustomType, registerCustomEnumeration, registerCustomEnumerationValue

schema_org = load_schema_org()

schema_org = registerCustomType(schema_org, name="User", parent="Person", properties=[])
schema_org = registerCustomProperty(schema_org, name="userName", domain=["Person", "User"], range=["Text"])

schema_org = registerCustomEnumeration(schema_org, name="TaskStatus")
schema_org = registerCustomEnumerationValue(schema_org, enum_type="TaskStatus", value="TaskStatusActive")
schema_org = registerCustomProperty(schema_org, name="taskStatus", domain=["User"], range=["TaskStatus"])

schema_validator = AloeSchemaValidator(schema_org)

schema_validator.IsEnumerationType("TaskStatus")                                           # True
schema_validator.EnumerationValueIsOfType("TaskStatus", "TaskStatusActive")               # True
schema_validator.Validate(subject_type_name="User", property_type_name="taskStatus", enumeration_value_name="TaskStatusActive")  # True
```

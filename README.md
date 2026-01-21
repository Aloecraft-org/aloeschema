# AloeSchema

<div align="center">

<img src="doc/icon.png" style="height:96px; width:96px;"/>

**A Schema.org Multitool**
</div>

## Getting Started

See **quickstart.ipynb** for more detailed usage examples

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

**Extending Schema.org With Custom Types and Properties**

use `registerCustomType` and `registerCustomProperty` to extend Schema.org with custom types and properties

``` py
from aloeschema.validator import AloeSchemaValidator
from aloeschema import load_schema_org, registerCustomProperty, registerCustomType

schema_org = load_schema_org()

schema_org = registerCustomType(schema_org, name="User", parent="Person", properties=[])
schema_org = registerCustomProperty(schema_org, name:="userName",   domain=["Person", "User"], range=["Text"])

schema_validator =  AloeSchemaValidator(schema_org)

print(f"""
Custom Property: `userName`
Description: {schema_validator._getProperty("userName", ignore_case=True)}
""")
```
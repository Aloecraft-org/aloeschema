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

from enum import StrEnum

class AloeSchemaErrorType(StrEnum):
    TYPE_NOT_RECOGNIZED = "TYPE_NOT_RECOGNIZED"
    PROPERTY_TYPE_NOT_RECOGNIZED = "PROPERTY_TYPE_NOT_RECOGNIZED"
    VALUE_TYPE_NOT_RECOGNIZED = "VALUE_TYPE_NOT_RECOGNIZED"
    PROPERTY_RANGE_TYPE_NOT_RECOGNIZED = "PROPERTY_RANGE_TYPE_NOT_RECOGNIZED"
    TYPE_NOT_IN_PROPERTY_RANGE = "TYPE_NOT_IN_PROPERTY_RANGE"
    TYPE_NOT_IN_PROPERTY_DOMAIN = "TYPE_NOT_IN_PROPERTY_DOMAIN"
    VALUE_TYPE_NOT_IN_PROPERTY_RANGE = "VALUE_TYPE_NOT_IN_PROPERTY_RANGE"
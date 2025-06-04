from typing import Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import Draft7Validator


class NOTAMSchema:
    def __init__(self):
        self.notam_schema = {
            "type": "object",
            "properties": {
                "state": {
                    "type": "string",
                },
                "id": {
                    "type": "string",
                    "minLength": 1
                },
                "notam_type": {
                    "type": "string",
                    "enum": ["NEW", "REPLACE", "CANCEL"]
                },
                "fir": {
                    "type": "string",
                    "pattern": "^[A-Z]{4}$"
                },
                "notam_code": {
                    "type": "string",
                    "pattern": "^[A-Z]{5}$"
                },
                "entity": {
                    "type": "string",
                    "pattern": "^[A-Z]{2}$"
                },
                "status": {
                    "type": "string",
                    "pattern": "^[A-Z]{2}$"
                },
                "category_area": {
                    "type": "string",
                },
                "sub_area": {
                    "type": "string",
                },
                "subject": {
                    "type": "string",
                },
                "condition": {
                    "type": "string",
                },
                "modifier": {
                    "type": "string",
                },
                "area_affected": {
                    "type": "object",
                    "properties": {
                        "lat": {
                            "type": "string",
                        },
                        "long": {
                            "type": "string",
                        },
                        "radius": {
                            "type": "number",
                            "minimum": 0
                        }
                    },
                    "required": ["lat", "long", "radius"]
                },
                "location": {
                    "type": "string",
                    "pattern": "^[A-Z]{4}$"
                },
                "valid_from": {
                    "type": "string",
                    "format": "date-time"
                },
                "valid_till": {
                    "type": "string",
                    "format": "date-time"
                },
                "schedule": {
                    "type": ["string", "null"]
                },
                "body": {
                    "type": "string",
                },
                "lower_limit": {
                    "type": ["string", "null"]
                },
                "upper_limit": {
                    "type": ["string", "null"]
                }
            },
            "dependentRequired": {
                "notam_code": ["entity","status","category_area","sub_area","subject","condition","modifier"]
            },
            "required": ["id", "notam_type", "notam_code", "body", "valid_till", "valid_from", "fir"]
        }

    def validate(self, notam_json: Dict) -> bool:
        try:
            validate(instance=notam_json, schema=self.notam_schema)
            return True
        except ValidationError as e:
            print(f"Validation Error: {e.message}")
            return False

    def validate_detail(self, notam_json: Dict) -> bool:
        validator = Draft7Validator(self.notam_schema)
        errors = list(validator.iter_errors(notam_json))

        if not errors:
            return True

        print(f"Found {len(errors)} validation error(s):")
        for error in errors:
            path = list(error.path)
            location = '.'.join(str(p) for p in path) if path else "(root)"
            print(f"- Field: {location}")
            print(f"  --->Message: {error.message}")
            print(f"  --->Invalid value: {error.instance}")

        return False

    def missing_value_notam(self, notam_json: Dict) -> Dict:
        json = {}
        properties = self.notam_schema["properties"]

        for field_name, field_def in properties.items():
            if field_name in notam_json:
                json[field_name] = notam_json[field_name]
            else:
                field_type = field_def.get("type")
                if isinstance(field_type, list):
                    json[field_name] = None
                elif field_type == "string":
                    json[field_name] = ""
                elif field_type == "number":
                    json[field_name] = 0
                elif field_type == "object":
                    json[field_name] = {}
                elif field_type == "array":
                    json[field_name] = []
                else:
                    json[field_name] = None

        return json


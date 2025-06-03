from typing import Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import Draft7Validator


class NOTAMSchema:
    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "state": {"type": "string"},
                "id": {"type": "string"},
                "notam_type": {"type": "string"},
                "fir": {"type": "string"},
                "notam_code": {"type": "string"},
                "entity": {"type": "string"},
                "status": {"type": "string"},
                "category_area": {"type": "string"},
                "sub_area": {"type": "string"},
                "subject": {"type": "string"},
                "condition": {"type": "string"},
                "modifier": {"type": "string"},
                "area_affected": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "string"},
                        "long": {"type": "string"},
                        "radius": {"type": "number"},
                    },
                    "required": ["lat", "long", "radius"]
                },
                "location": {"type": "string"},
                "valid_from": {"type": ["string", "null"]},
                "valid_till": {"type": ["string", "null"]},
                "schedule": {"type": "string"},
                "body": {"type": "string"},
                "lower_limit": {"type": ["string","null"]},
                "upper_limit": {"type": ["string","null"]}
            },
            "required": ["id", "notam_type", "notam_code"]
        }

    def validate(self, notam_json: Dict) -> bool:
        try:
            validate(instance=notam_json, schema=self.schema)
            return True
        except ValidationError as e:
            print(f"Validation Error: {e.message}")
            return False

    def validate_detail(self, notam_json: Dict) -> bool:
        validator = Draft7Validator(self.schema)
        errors = list(validator.iter_errors(notam_json))

        if not errors:
            return True

        print(f"Found {len(errors)} validation error(s):")
        for error in errors:
            path = list(error.path)
            location = '.'.join(str(p) for p in path) if path else "(root)"
            print(f"- Field: {location}")
            print(f"  → Message: {error.message}")
            print(f"  → Invalid value: {error.instance}")

        return False

    def missing_value_notam(self,notam_json: Dict) -> Dict:
        sanitized = {}
        properties = self.schema["properties"]

        for field_name, field_def in properties.items():
            if field_name in notam_json:
                sanitized[field_name] = notam_json[field_name]
            else:
                field_type = field_def.get("type")
                if isinstance(field_type, list):
                    sanitized[field_name] = None
                elif field_type == "string":
                    sanitized[field_name] = ""
                elif field_type == "number":
                    sanitized[field_name] = 0
                elif field_type == "object":
                    sanitized[field_name] = {}
                elif field_type == "array":
                    sanitized[field_name] = []
                else:
                    sanitized[field_name] = None

        return sanitized
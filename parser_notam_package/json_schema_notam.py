from typing import Dict
from jsonschema import validate, ValidationError
from jsonschema.validators import Draft7Validator
import json
import re
from pypdf import PdfReader

from parser_notam_package import NOTAMParser


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
                "referenced_notam": {
                    "type": ["string", "null"],
                    "pattern": "^[A-Z]\\d{4}/\\d{2}$"  # Pattern for NOTAM ID format like A1234/24
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
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "notam_type": {"const": "NEW"}
                        }
                    },
                    "then": {
                        "properties": {
                            "referenced_notam": {"type": "null"}
                        }
                    }
                },
                {
                    "if": {
                        "properties": {
                            "notam_type": {"const": "REPLACE"}
                        }
                    },
                    "then": {
                        "properties": {
                            "referenced_notam": {
                                "type": "string",
                                "pattern": "^[A-Z]\\d{4}/\\d{2}$"
                            }
                        },
                        "required": ["referenced_notam"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "notam_type": {"const": "CANCEL"}
                        }
                    },
                    "then": {
                        "properties": {
                            "referenced_notam": {
                                "type": "string",
                                "pattern": "^[A-Z]\\d{4}/\\d{2}$"
                            }
                        },
                        "required": ["referenced_notam"]
                    }
                }
            ],
            "dependentRequired": {
                "notam_code": ["entity", "status", "category_area", "sub_area", "subject", "condition", "modifier"]
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

    def process_and_validate_pdf(self, pdf_path: str, output_json_path: str):
        """
        Read file PDF Notam, validate all the notam in PDF file
        Write Notam valid, print ID of Notam Invalid

        Args:
            pdf_path (str): Path to pdf Notam file
            output_json_path (str): Path to save Json
        """
        parser = NOTAMParser()
        print(f"Reading pdf file from {pdf_path}...")
        try:
            reader = PdfReader(pdf_path)
            full_text = "\n".join([page.extract_text() for page in reader.pages])
        except FileNotFoundError:
            print(f"Can't find pdf file in'{pdf_path}'.")
            return
        except Exception as e:
            print(f"Error read pdf file")
            return
        notam_texts = re.split(r'\n(?=[A-Z]\d{4}/\d{2}\s+NOTAM)', full_text)
        notam_texts = [notam.strip() for notam in notam_texts if notam.strip()]

        if not notam_texts:
            print("Can't file notam in pdf file.")
            return

        print(f"Find {len(notam_texts)} notam")

        valid_notams_json = []
        invalid_notam_ids = []
        for notam_text in notam_texts:
            notam_id = parser.parse_notam_id(notam_text)
            if not notam_id:
                print(f"Pass notam with invalid ID  '{notam_text[:60]}...'")
                continue
            try:
                notam_json = parser.to_json(notam_text)
                if self.validate(notam_json):
                    valid_notams_json.append(notam_json)
                else:
                    invalid_notam_ids.append(notam_id)

            except Exception as e:
                print(f" lỗi khi phân tích NOTAM {notam_id}: {e}")
                invalid_notam_ids.append(notam_id)

        if valid_notams_json:
            print(f"\nWrite {len(valid_notams_json)} notam valid: {output_json_path}")
            try:
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(valid_notams_json, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error write json")
        else:
            print("\nDon't have invalid notam in PDF file")

        if invalid_notam_ids:
            print("\n-------------------------------------------------")
            print(f"Invalid Notam:")
            for invalid_id in set(invalid_notam_ids):
                print(f"   - ID: {invalid_id}")
        print("Complete")


import sys
import os
import json
import yaml
from openapi_spec_validator import validate_spec
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

def main():
    spec_path = "openapi.yaml"
    if not os.path.exists(spec_path):
        print(f"Error: {spec_path} not found.")
        sys.exit(1)
        
    print(f"Loading and validating {spec_path}...")
    with open(spec_path, "r", encoding="utf-8") as f:
        try:
            spec = yaml.safe_load(f)
        except Exception as e:
            print(f"Error parsing YAML: {e}")
            sys.exit(1)
            
    # Validate OpenAPI Spec
    try:
        validate_spec(spec)
        print("OK: OpenAPI specification is valid!")
    except Exception as e:
        print(f"ERROR: OpenAPI specification validation failed:\n{e}")
        sys.exit(1)
        
    # Setup Registry for JSON Schema Validation
    # Explicitly use DRAFT202012 since OpenAPI 3.1.0 uses it.
    resource = Resource(contents=spec, specification=DRAFT202012)
    registry = Registry().with_resource("file:///openapi.json", resource)
    
    # Examples to validate
    examples = [
        {
            "file": "examples/predict-request.json",
            "schema_ref": "file:///openapi.json#/components/schemas/PredictRequest"
        },
        {
            "file": "examples/predict-response.json",
            "schema_ref": "file:///openapi.json#/components/schemas/PredictResponse"
        },
        {
            "file": "examples/predict-error-413.json",
            "schema_ref": "file:///openapi.json#/components/schemas/Error"
        },
        {
            "file": "examples/batch-request.json",
            "schema_ref": "file:///openapi.json#/components/schemas/BatchPredictRequest"
        },
        {
            "file": "examples/batch-response.json",
            "schema_ref": "file:///openapi.json#/components/schemas/BatchPredictResponse"
        }
    ]
    
    has_errors = False
    for ex in examples:
        path = ex["file"]
        ref = ex["schema_ref"]
        
        if not os.path.exists(path):
            print(f"Warning: Example file {path} not found yet.")
            continue
            
        print(f"Validating {path} against schema {ref.split('#')[-1]}...")
        with open(path, "r", encoding="utf-8") as f:
            try:
                instance = json.load(f)
            except Exception as e:
                print(f"  ERROR: JSON Parse Error in {path}: {e}")
                has_errors = True
                continue
                
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": ref
        }
        
        try:
            validator = Draft202012Validator(schema, registry=registry)
            validator.validate(instance)
            print(f"  OK: {path} is valid!")
        except Exception as e:
            print(f"  ERROR: Validation failed for {path}:\n{e}")
            has_errors = True
            
    if has_errors:
        print("\nSome validations failed.")
        sys.exit(1)
    else:
        print("\nAll validations passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

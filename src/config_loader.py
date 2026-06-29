import json

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def apply_config(record, config):
    """
    Project/rename fields based on config.
    Supports omitting or nulling missing fields.
    """
    output = {}
    on_missing = config.get("on_missing", "null")

    for field_def in config.get("fields", []):
        src = field_def.get("from")
        dst = field_def.get("path")
        value = record.get(src)

        if value is None or value == [] or value == {}:
            if on_missing == "omit":
                continue
            value = None

        output[dst] = value

    if config.get("include_confidence", True):
        output["overall_confidence"] = record.get("overall_confidence")

    if config.get("include_provenance", True):
        output["provenance"] = record.get("provenance", [])

    return output
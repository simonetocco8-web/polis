import json
import math
from functools import lru_cache

from .registry import SCHEMA, identifier, require


@lru_cache
def schema():
    return json.loads(SCHEMA.read_bytes())


def _validate(value, rule):
    if "$ref" in rule:
        _validate(value, schema()["$defs"]["id"])
        return
    kind = rule.get("type")
    if isinstance(kind, list):
        require(type(value) in (int, float, bool) and (type(value) is not float or math.isfinite(value)),
                "Parametro Methodos non numerico")
    elif kind == "object":
        require(type(value) is dict, "Oggetto Methodos richiesto")
        properties = rule.get("properties", {})
        require(set(rule.get("required", ())) <= value.keys(), "Campi Methodos mancanti")
        require(len(value) <= rule.get("maxProperties", len(value)), "Troppi parametri")
        for key, item in value.items():
            if "propertyNames" in rule:
                _validate(key, rule["propertyNames"])
            child = properties.get(key, rule.get("additionalProperties", False))
            require(child is not False, "Campo Methodos sconosciuto")
            _validate(item, child)
    elif kind == "array":
        require(type(value) is list and rule["minItems"] <= len(value) <= rule["maxItems"], "Lista Methodos non valida")
        for item in value:
            _validate(item, rule["items"])
        if rule.get("uniqueItems"):
            require(len(set(value)) == len(value), "Duplicati Methodos")
    elif kind == "integer":
        require(type(value) is int and value >= rule["minimum"], "Intero Methodos non valido")
    elif kind == "string":
        if "pattern" in rule:
            identifier(value)
        else:
            require(isinstance(value, str) and rule["minLength"] <= len(value) <= rule["maxLength"] and value.strip(),
                    "Testo Methodos non valido")
    else:
        require("const" in rule, "Regola Methodos non riconosciuta")
        require(value == rule["const"], "Versione Methodos non valida")


def validate(proposal):
    _validate(proposal, schema())

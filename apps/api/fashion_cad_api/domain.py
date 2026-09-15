from __future__ import annotations

from typing import Any


def missing_fields(document: dict[str, Any]) -> list[str]:
    measurements = document["measurements_mm"]
    if document["product_type"] == "laptop_bag":
        fields = ["laptop_width_mm", "laptop_height_mm", "laptop_depth_mm"]
        return [field for field in fields if not measurements.get(field)]
    fields = ["chest_mm", "body_length_mm"]
    return [field for field in fields if not measurements.get(field)]


def to_response(document: dict[str, Any]) -> dict[str, Any]:
    response = dict(document)
    response["missing"] = missing_fields(document)
    return response

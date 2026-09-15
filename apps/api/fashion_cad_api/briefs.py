from __future__ import annotations

import re
from typing import Any

from .schemas import BriefRequest


def analyze_local_brief(request: BriefRequest) -> dict[str, Any]:
    text = request.description.lower()
    is_bag = request.product_type == "laptop_bag" or any(word in text for word in ("bolso", "funda", "laptop", "mochila"))
    product_type = "laptop_bag" if is_bag else "upper_garment"
    components = []
    if "bolsillo" in text:
        components.append("pocket")
    if "cierre" in text or "zipper" in text:
        components.append("zipper")
    if "correa" in text or "asa" in text:
        components.append("strap")
    materials = []
    if "recicl" in text:
        materials.append("recycled material (evidence required)")
    if "nylon" in text:
        materials.append("nylon")
    if "algodón" in text or "algodon" in text:
        materials.append("cotton")
    confirmed: dict[str, Any] = {"components": components, "materials": materials}
    estimated: dict[str, Any] = {}
    missing: list[str] = []
    dimensions = re.search(r"(\d{2,3})\s*[x×]\s*(\d{2,3})\s*[x×]\s*(\d{1,2})\s*mm", text)
    if product_type == "laptop_bag":
        if dimensions:
            width, height, depth = (int(item) for item in dimensions.groups())
            confirmed["measurements_mm"] = {"laptop_width_mm": width, "laptop_height_mm": height, "laptop_depth_mm": depth}
        else:
            missing = ["laptop_width_mm", "laptop_height_mm", "laptop_depth_mm"]
            estimated["padding_allowance_mm"] = 18
    else:
        missing = ["chest_mm", "body_length_mm"]
        estimated["ease_mm"] = 80
    question = None
    if missing and product_type == "laptop_bag":
        question = "¿Cuál es el ancho, alto y espesor máximos de la laptop en mm, o cuál es su modelo exacto?"
    elif missing:
        question = "¿Cuál es el contorno de pecho y el largo de prenda objetivo en mm?"
    return {"product_type": product_type, "confirmed": confirmed, "estimated": estimated, "missing": missing, "next_question": question}

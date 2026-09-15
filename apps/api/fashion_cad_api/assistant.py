from __future__ import annotations

import re
from typing import Any

from .schemas import OperationRequest


QUESTION_WORDS = ("qué falta", "que falta", "qué medidas", "que medidas", "estado", "ayuda", "cómo", "como")
COMPONENTS = (
    ("bolsillo", "bolsillo frontal"),
    ("cierre", "cierre negro"),
    ("zipper", "cierre negro"),
    ("correa", "correa"),
    ("asa", "asa"),
    ("cuello", "cuello rib"),
)
MATERIALS = (
    ("nylon reciclado", "nylon reciclado"),
    ("nylon", "nylon"),
    ("algodón reciclado", "algodón reciclado"),
    ("algodon reciclado", "algodón reciclado"),
    ("algodón", "algodón"),
    ("algodon", "algodón"),
    ("rpet", "RPET"),
    ("piñatex", "Piñatex"),
)


def _has_component(document: dict[str, Any], component: str) -> bool:
    normalized = component.lower()
    return any(normalized in str(existing).lower() or str(existing).lower() in normalized for existing in document["components"])


def plan_local_message(document: dict[str, Any], message: str) -> tuple[list[OperationRequest], str]:
    """Turn a constrained Spanish design instruction into traceable local revisions.

    This is intentionally deterministic until a separately benchmarked local model
    is installed. Questions do not mutate a design.
    """
    text = " ".join(message.lower().split())
    if any(marker in text for marker in QUESTION_WORDS) or text.endswith("?"):
        missing = document.get("missing", [])
        if missing:
            return [], f"Falta confirmar: {', '.join(missing)}. Podés dictarme las medidas en milímetros."
        return [], "El diseño tiene sus datos técnicos mínimos. Podés pedirme agregar componentes, materiales o exportar."

    operations: list[OperationRequest] = []
    for keyword, component in COMPONENTS:
        if keyword in text and not _has_component(document, component):
            operations.append(OperationRequest(kind="add_component", value=component, note="Asistente local: componente solicitado."))

    requested_materials = [material for keyword, material in MATERIALS if keyword in text]
    if requested_materials:
        merged = list(dict.fromkeys([*document["materials"], *requested_materials]))
        if merged != document["materials"]:
            operations.append(OperationRequest(kind="set_materials", value=merged, note="Asistente local: materiales solicitados."))

    dimensions = re.search(r"(\d{2,4})\s*[x×]\s*(\d{2,4})\s*[x×]\s*(\d{1,3})\s*(?:mm)?", text)
    if dimensions and document["product_type"] == "laptop_bag":
        for name, value in zip(("laptop_width_mm", "laptop_height_mm", "laptop_depth_mm"), dimensions.groups(), strict=True):
            if float(document["measurements_mm"].get(name) or 0) != float(value):
                operations.append(OperationRequest(kind="set_measurement", value=f"{name}:{value}", note="Asistente local: medida indicada por usuario."))

    edit_words = ("cambiá", "cambia", "actualizá", "actualiza", "rediseñá", "rediseña", "hacé", "hace", "quiero")
    if not operations and any(word in text for word in edit_words):
        operations.append(OperationRequest(kind="set_description", value=message, note="Asistente local: dirección de diseño."))

    if not operations:
        return [], "No detecté una modificación segura. Probá: ‘agregá bolsillo y cierre’, ‘usá nylon reciclado’ o ‘355 × 245 × 25 mm’."
    return operations, f"Aplicaré {len(operations)} cambio(s) locales y crearé revisiones trazables."

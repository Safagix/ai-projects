from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from .config import settings

MM_TO_M = 0.001


def _colour(document: dict[str, Any]) -> tuple[int, int, int, int]:
    materials = " ".join(document.get("materials", [])).lower()
    if "recicl" in materials:
        return (37, 61, 56, 255)
    if "algod" in materials or "cotton" in materials:
        return (215, 201, 174, 255)
    return (62, 69, 76, 255)


def _add_box(
    scene: trimesh.Scene,
    name: str,
    extents_mm: tuple[float, float, float],
    position_mm: tuple[float, float, float],
    colour: tuple[int, int, int, int],
    rotation_z: float = 0.0,
) -> None:
    mesh = trimesh.creation.box(extents=np.array(extents_mm) * MM_TO_M)
    mesh.visual.material = trimesh.visual.material.SimpleMaterial(diffuse=np.array(colour, dtype=np.uint8))
    transform = trimesh.transformations.rotation_matrix(rotation_z, [0, 0, 1])
    transform[:3, 3] = np.array(position_mm) * MM_TO_M
    mesh.apply_transform(transform)
    scene.add_geometry(mesh, geom_name=name, node_name=name)


def _has_component(document: dict[str, Any], *terms: str) -> bool:
    components = " ".join(document.get("components", [])).lower()
    return any(term in components for term in terms)


def _tshirt_scene(document: dict[str, Any]) -> trimesh.Scene:
    measurements = document["measurements_mm"]
    chest_circumference = float(measurements.get("chest_mm") or 1120)
    length = float(measurements.get("body_length_mm") or 720)
    width = chest_circumference / 2
    colour = _colour(document)
    accent = (16, 22, 19, 255)
    scene = trimesh.Scene()
    _add_box(scene, "body", (width, 55, length), (0, 0, length / 2), colour)
    sleeve_width = width * 0.34
    _add_box(scene, "left-sleeve", (sleeve_width, 48, 240), (-(width + sleeve_width) / 2 + 30, 0, length * 0.71), colour, 0.18)
    _add_box(scene, "right-sleeve", (sleeve_width, 48, 240), ((width + sleeve_width) / 2 - 30, 0, length * 0.71), colour, -0.18)
    neck = trimesh.creation.cylinder(radius=95 * MM_TO_M, height=56 * MM_TO_M, sections=32)
    neck.visual.material = trimesh.visual.material.SimpleMaterial(diffuse=np.array(accent, dtype=np.uint8))
    neck.apply_translation([0, 0, (length - 20) * MM_TO_M])
    scene.add_geometry(neck, geom_name="neck", node_name="neck")
    if _has_component(document, "bolsillo", "pocket"):
        _add_box(scene, "front-pocket", (width * 0.28, 8, length * 0.22), (-width * 0.22, -32, length * 0.42), accent)
    if _has_component(document, "cierre", "zipper"):
        _add_box(scene, "zipper", (8, 8, length * 0.55), (0, -34, length * 0.5), accent)
    return scene


def _bag_scene(document: dict[str, Any]) -> trimesh.Scene:
    measurements = document["measurements_mm"]
    width = float(measurements.get("laptop_width_mm") or 355) + 36
    height = float(measurements.get("laptop_height_mm") or 245) + 36
    depth = float(measurements.get("laptop_depth_mm") or 25) + 30
    colour = _colour(document)
    accent = (214, 164, 90, 255)
    scene = trimesh.Scene()
    _add_box(scene, "body", (width, depth, height), (0, 0, height / 2), colour)
    _add_box(scene, "front-pocket", (width * 0.8, 10, height * 0.42), (0, -depth / 2 - 8, height * 0.42), accent)
    if _has_component(document, "cierre", "zipper"):
        _add_box(scene, "zipper", (width * 0.92, 10, 10), (0, -depth / 2 - 10, height * 0.93), (20, 20, 20, 255))
    if _has_component(document, "correa", "strap", "asa", "handle"):
        _add_box(scene, "left-handle", (18, 18, height * 0.42), (-width * 0.23, 0, height * 1.1), accent, -0.35)
        _add_box(scene, "right-handle", (18, 18, height * 0.42), (width * 0.23, 0, height * 1.1), accent, 0.35)
    return scene


def export_mockup(document: dict[str, Any]) -> list[str]:
    base = settings.artifacts_dir / "mockups" / document["id"] / f"rev-{document['revision']}"
    base.mkdir(parents=True, exist_ok=True)
    scene = _bag_scene(document) if document["product_type"] == "laptop_bag" else _tshirt_scene(document)
    glb_path = base / "mockup.glb"
    metadata_path = base / "mockup-metadata.json"
    glb_path.write_bytes(scene.export(file_type="glb"))
    metadata_path.write_text(
        json.dumps(
            {
                "design_id": document["id"],
                "revision": document["revision"],
                "product_type": document["product_type"],
                "units": "m",
                "source": "parametric_local",
                "measurements_mm": document["measurements_mm"],
                "components": document["components"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return [str(glb_path.relative_to(settings.artifacts_dir)), str(metadata_path.relative_to(settings.artifacts_dir))]
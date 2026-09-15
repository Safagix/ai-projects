from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import ceil
from pathlib import Path
from typing import Any

import svgwrite
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .config import settings


@dataclass(frozen=True)
class PatternPiece:
    name: str
    points: list[tuple[float, float]]
    quantity: int
    material: str
    grainline: tuple[tuple[float, float], tuple[float, float]]
    cut_on_fold: bool = False


def _has_component(document: dict[str, Any], *terms: str) -> bool:
    components = " ".join(document.get("components", [])).lower()
    return any(term in components for term in terms)


def _piece(name: str, points: list[tuple[float, float]], quantity: int, material: str, cut_on_fold: bool = False) -> PatternPiece:
    x, y = points[0]
    return PatternPiece(name, points, quantity, material, ((x + 20, y + 20), (x + 20, y + 120)), cut_on_fold)


def _tshirt(document: dict[str, Any]) -> list[PatternPiece]:
    measurements = document["measurements_mm"]
    chest = float(measurements.get("chest_mm") or 1120) / 2
    length = float(measurements.get("body_length_mm") or 720)
    front = [(30, 30), (30 + chest, 30), (30 + chest, 30 + length), (30, 30 + length)]
    back = [(40 + chest, 30), (40 + chest * 2, 30), (40 + chest * 2, 30 + length), (40 + chest, 30 + length)]
    sleeve = [(30, 30 + length + 20), (30 + chest * 0.52, 30 + length + 20), (30 + chest * 0.44, 30 + length + 210), (30 + chest * 0.08, 30 + length + 210)]
    pieces = [_piece("Front", front, 1, "main"), _piece("Back", back, 1, "main"), _piece("Sleeve", sleeve, 2, "main")]
    if _has_component(document, "cuello", "collar", "neck"):
        neckband = [(30 + chest * 0.58, 30 + length + 20), (30 + chest * 0.88, 30 + length + 20), (30 + chest * 0.88, 30 + length + 90), (30 + chest * 0.58, 30 + length + 90)]
        pieces.append(_piece("Neckband", neckband, 1, "rib"))
    if _has_component(document, "bolsillo", "pocket"):
        pocket = [(30 + chest * 0.1, 30 + length + 120), (30 + chest * 0.38, 30 + length + 120), (30 + chest * 0.38, 30 + length + 320), (30 + chest * 0.1, 30 + length + 320)]
        pieces.append(_piece("Chest pocket", pocket, 1, "main"))
    return pieces


def _laptop_bag(document: dict[str, Any]) -> list[PatternPiece]:
    measurements = document["measurements_mm"]
    width = float(measurements.get("laptop_width_mm") or 355) + 36
    height = float(measurements.get("laptop_height_mm") or 245) + 36
    depth = float(measurements.get("laptop_depth_mm") or 25) + 30
    front = [(30, 30), (30 + width, 30), (30 + width, 30 + height), (30, 30 + height)]
    back = [(50 + width, 30), (50 + width * 2, 30), (50 + width * 2, 30 + height), (50 + width, 30 + height)]
    gusset = [(30, 50 + height), (30 + 2 * (width + height), 50 + height), (30 + 2 * (width + height), 50 + height + depth), (30, 50 + height + depth)]
    pieces = [_piece("Outer front", front, 1, "outer"), _piece("Outer back", back, 1, "outer"), _piece("Gusset", gusset, 1, "outer")]
    if _has_component(document, "bolsillo", "pocket"):
        pocket = [(30, 80 + height + depth), (30 + width * 0.8, 80 + height + depth), (30 + width * 0.8, 80 + height + depth + height * 0.45), (30, 80 + height + depth + height * 0.45)]
        pieces.append(_piece("Front pocket", pocket, 1, "outer"))
    if _has_component(document, "correa", "strap", "asa", "handle"):
        strap = [(30, 110 + height + depth), (30 + 700, 110 + height + depth), (30 + 700, 110 + height + depth + 38), (30, 110 + height + depth + 38)]
        pieces.append(_piece("Shoulder strap", strap, 1, "webbing"))
    if _has_component(document, "cierre", "zipper"):
        zipper = [(30, 170 + height + depth), (30 + 2 * width + 2 * height, 170 + height + depth), (30 + 2 * width + 2 * height, 170 + height + depth + 20), (30, 170 + height + depth + 20)]
        pieces.append(_piece("Zipper binding", zipper, 1, "zipper"))
    return pieces


def pieces_for(document: dict[str, Any]) -> list[PatternPiece]:
    return _laptop_bag(document) if document["product_type"] == "laptop_bag" else _tshirt(document)


def bounds(pieces: list[PatternPiece]) -> tuple[float, float]:
    x_values = [point[0] for piece in pieces for point in piece.points]
    y_values = [point[1] for piece in pieces for point in piece.points]
    return max(x_values) + 30, max(y_values) + 30


def write_svg(document: dict[str, Any], destination: Path) -> None:
    pieces = pieces_for(document)
    width, height = bounds(pieces)
    drawing = svgwrite.Drawing(str(destination), size=(f"{width}mm", f"{height}mm"), viewBox=f"0 0 {width} {height}")
    drawing.set_desc(title=f"{document['name']} revision {document['revision']}", desc="Pattern units are millimetres. Print at 100 percent.")
    drawing.add(drawing.rect(insert=(0, 0), size=(width, height), fill="white"))
    drawing.add(drawing.rect(insert=(10, 10), size=(100, 100), fill="none", stroke="#111", stroke_width=0.6))
    drawing.add(drawing.text("CONTROL 100 mm", insert=(10, 116), font_size="5px"))
    for piece in pieces:
        drawing.add(drawing.polygon(points=piece.points, fill="none", stroke="#161616", stroke_width=0.8))
        x, y = piece.points[0]
        cut_note = "cut on fold" if piece.cut_on_fold else f"cut {piece.quantity}"
        drawing.add(drawing.text(f"{piece.name} · {cut_note} · {piece.material}", insert=(x + 5, y + 12), font_size="6px"))
        drawing.add(drawing.line(start=piece.grainline[0], end=piece.grainline[1], stroke="#e85d2a", stroke_width=0.6))
        drawing.add(drawing.text("GRAIN", insert=(piece.grainline[0][0] + 3, piece.grainline[0][1] + 15), font_size="4px", fill="#e85d2a"))
    drawing.save()


def _write_tiled_pdf(document: dict[str, Any], destination: Path, page_width: float, page_height: float, label: str) -> None:
    pieces = pieces_for(document)
    width, height = bounds(pieces)
    overlap = 10
    header_height = 130
    printable_width, printable_height = page_width - overlap, page_height - header_height
    columns, rows = ceil(width / printable_width), ceil(height / printable_height)
    pdf = canvas.Canvas(str(destination), pagesize=(page_width * mm, page_height * mm))
    for row in range(rows):
        for col in range(columns):
            origin_x, origin_y = col * printable_width, row * printable_height
            page_number = row * columns + col + 1
            pdf.setFont("Helvetica", 7)
            pdf.drawString(10 * mm, (page_height - 10) * mm, f"{document['name']} · rev {document['revision']} · {label} · hoja {page_number}/{rows * columns}")
            pdf.drawString(10 * mm, (page_height - 17) * mm, "Imprimir al 100 %. Verificar el cuadrado de 100 mm antes de cortar.")
            control_x, control_y = page_width - 110, page_height - 120
            pdf.rect(control_x * mm, control_y * mm, 100 * mm, 100 * mm)
            pdf.drawString(control_x * mm, (control_y - 4) * mm, "CONTROL 100 mm")
            pdf.saveState()
            clip = pdf.beginPath()
            clip.rect(0, 0, page_width * mm, printable_height * mm)
            pdf.clipPath(clip, stroke=0, fill=0)
            pdf.translate(-origin_x * mm, -origin_y * mm)
            for piece in pieces:
                path = pdf.beginPath()
                first_x, first_y = piece.points[0]
                path.moveTo(first_x * mm, first_y * mm)
                for x, y in piece.points[1:]:
                    path.lineTo(x * mm, y * mm)
                path.close()
                pdf.setStrokeColorRGB(0.08, 0.08, 0.08)
                pdf.drawPath(path, stroke=1, fill=0)
                pdf.setFont("Helvetica", 6)
                pdf.drawString((first_x + 5) * mm, (first_y + 8) * mm, piece.name)
                pdf.setStrokeColorRGB(0.91, 0.36, 0.16)
                (gx1, gy1), (gx2, gy2) = piece.grainline
                pdf.line(gx1 * mm, gy1 * mm, gx2 * mm, gy2 * mm)
            pdf.restoreState()
            pdf.showPage()
    pdf.save()


def write_tiled_pdf(document: dict[str, Any], destination: Path) -> None:
    _write_tiled_pdf(document, destination, 210, 297, "A4 tiled")


def write_a0_pdf(document: dict[str, Any], destination: Path) -> None:
    _write_tiled_pdf(document, destination, 1189, 841, "A0")


def export_pattern(document: dict[str, Any]) -> list[str]:
    base = settings.artifacts_dir / "patterns" / document["id"] / f"rev-{document['revision']}"
    base.mkdir(parents=True, exist_ok=True)
    svg_path = base / "pattern.svg"
    a4_path = base / "pattern-a4-tiled.pdf"
    a0_path = base / "pattern-a0.pdf"
    metadata_path = base / "pattern-metadata.json"
    write_svg(document, svg_path)
    write_tiled_pdf(document, a4_path)
    write_a0_pdf(document, a0_path)
    metadata_path.write_text(
        json.dumps(
            {
                "design_id": document["id"],
                "revision": document["revision"],
                "units": "mm",
                "calibration_mm": 100,
                "a4_overlap_mm": 10,
                "pieces": [asdict(piece) for piece in pieces_for(document)],
                "validation_required": "Physical sample and seam allowance validation are required before production.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return [str(path.relative_to(settings.artifacts_dir)) for path in (svg_path, a4_path, a0_path, metadata_path)]
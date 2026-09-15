from __future__ import annotations

import os
from pathlib import Path


class Settings:
    project_root = Path(os.getenv("FASHION_CAD_ROOT", r"D:\Digital Lab\FashionCAD"))
    data_dir = Path(os.getenv("FASHION_CAD_DATA_DIR", project_root / "data"))
    artifacts_dir = Path(os.getenv("FASHION_CAD_ARTIFACTS_DIR", project_root / "artifacts"))
    allowed_origins = os.getenv("FASHION_CAD_ALLOWED_ORIGINS", "http://127.0.0.1:5173").split(",")
    operator_enabled = os.getenv("FASHION_CAD_OPERATOR_ENABLED", "false").lower() == "true"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "sqlite" / "fashion_cad.db"

    @property
    def library_dir(self) -> Path:
        return self.project_root / "KNOWLEDGE_BASE_STUDIO"

    @property
    def lancedb_dir(self) -> Path:
        return self.data_dir / "lancedb"

    @property
    def model_manifest_path(self) -> Path:
        return self.project_root / "models" / "manifest.json"


settings = Settings()

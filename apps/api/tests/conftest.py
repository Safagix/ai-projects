import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    root = tmp_path / "FashionCAD"
    (root / "models").mkdir(parents=True)
    (root / "models" / "manifest.json").write_text('{"models": []}', encoding="utf-8")
    monkeypatch.setenv("FASHION_CAD_ROOT", str(root))
    monkeypatch.setenv("FASHION_CAD_DATA_DIR", str(root / "data"))
    monkeypatch.setenv("FASHION_CAD_ARTIFACTS_DIR", str(root / "artifacts"))
    from fashion_cad_api import main
    from fashion_cad_api.config import settings
    from fashion_cad_api.repository import Repository

    settings.project_root = root
    settings.data_dir = root / "data"
    settings.artifacts_dir = root / "artifacts"
    main.repository = Repository(settings.database_path)
    with TestClient(main.app) as test_client:
        yield test_client

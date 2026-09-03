import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, Request
from src.presentacion_reflex.api.pdf_download_api import (
    pdf_router,
    rate_limit_pdf,
    get_current_user,
)
import urllib.parse

pdf_api = FastAPI(dependencies=[Depends(rate_limit_pdf)])
pdf_api.include_router(pdf_router)

client = TestClient(pdf_api)


def mock_get_current_user(request: Request):
    return {"id": "test_user_123"}


@pytest.fixture
def setup_mock_user():
    pdf_api.dependency_overrides[get_current_user] = mock_get_current_user
    import src.presentacion_reflex.api.pdf_download_api as api_module

    api_module.RATE_LIMIT_DB.clear()
    yield
    pdf_api.dependency_overrides = {}
    api_module.RATE_LIMIT_DB.clear()


def test_descarga_pdf_exito(tmp_path, monkeypatch, setup_mock_user):
    import src.presentacion_reflex.api.pdf_download_api as api_module

    dummy_pdf = tmp_path / "contrato de mandato v2.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n...")

    monkeypatch.setattr(api_module, "PDF_OUTPUT_DIR", tmp_path)

    filename_encoded = urllib.parse.quote(dummy_pdf.name)
    response = client.get(f"/download/{filename_encoded}")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "filename*=utf-8" in response.headers["content-disposition"]


def test_descarga_pdf_404_inexistente(setup_mock_user):
    response = client.get("/download/archivo_que_no_existe.pdf")
    assert response.status_code == 404
    assert "no encontrado o expirado" in response.json()["detail"]


def test_descarga_pdf_rate_limit(setup_mock_user):
    for _ in range(10):
        client.get("/download/algonormal.pdf")

    response = client.get("/download/algonormal.pdf")
    assert response.status_code == 429
    assert "Rate Limit" in response.json()["detail"]


def test_descarga_pdf_path_traversal(setup_mock_user):
    payload = urllib.parse.quote("../../../../../etc/passwd")
    response = client.get(f"/download/{payload}")
    assert response.status_code in [403, 404]


def test_401_unauthorized():
    def fail_user(request: Request):
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Sesion requerida")

    pdf_api.dependency_overrides[get_current_user] = fail_user

    response = client.get("/download/test.pdf")
    assert response.status_code == 401

    pdf_api.dependency_overrides = {}

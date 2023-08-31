# tests/test_app.py#
from app import app

def test_app_runs():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert "DolFin | Landing" in response.data.decode('utf-8')
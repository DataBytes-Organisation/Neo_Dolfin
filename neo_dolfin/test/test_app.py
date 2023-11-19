# tests/test_app.py#
from app import app

def test_app_runs():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert "DolFin | Landing" in response.data.decode('utf-8')

def test_app_geolock():
    client = app.test_client()
    usa_header = {'REMOTE_ADDR': '185.169.0.168'}       # American IP
    aus_header = {'REMOTE_ADDR': '103.192.80.189'}      # Australian IP
    france_header = {'REMOTE_ADDR': '45.141.123.17'}    # French IP
    localhost_header = {'REMOTE_ADDR': '127.0.0.1'}     # Localhost IP
    response = client.get('/', environ_overrides=usa_header)
    assert response.status_code == 403
    assert "Sorry, you are restricted from accessing this content." in response.data.decode('utf-8')
    response = client.get('/', environ_overrides=france_header)
    assert response.status_code == 403
    assert "Sorry, you are restricted from accessing this content." in response.data.decode('utf-8')
    response = client.get('/', environ_overrides=aus_header)
    assert response.status_code == 200
    assert "DolFin | Landing" in response.data.decode('utf-8')
    response = client.get('/', environ_overrides=localhost_header)
    assert response.status_code == 200
    assert "DolFin | Landing" in response.data.decode('utf-8')
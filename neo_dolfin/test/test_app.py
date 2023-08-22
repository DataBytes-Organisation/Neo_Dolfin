# tests/test_app.py#
from app import app

def test_hello():
    os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-2'  # Replace with your desired AWS region
    client = app.test_client()

    response = client.get('/')
    assert response.status_code == 200
    assert "DolFin | Landing" in response.data.decode('utf-8')

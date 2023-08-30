import pytest
from rest_framework.test import APIClient





@pytest.mark.django_db
def test_add_user_upload_data():
    client = APIClient()
    response = client.post('/upload/', {'url': 'http://gw36.a-don.ru:8181/platform/shop1.yaml'})
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_user():
    pass
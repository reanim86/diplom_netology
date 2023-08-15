import pytest
from rest_framework.test import APIClient





@pytest.mark.django_db
def test_product_cards():
    client = APIClient()
    response = client.get('/api/products/')
    assert response.status_code == 200
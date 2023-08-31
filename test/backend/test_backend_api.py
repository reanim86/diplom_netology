import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from backend.models import User
import json


@pytest.mark.django_db
def test_add_user():
    count = User.objects.count()
    client = APIClient()
    data = json.dumps({'surname': 'kudino',
                        'first_name': 'Alekse',
                        'last_name': 'Ivanovch',
                        'email': 'a.kudino@a-don.ru',
                        'password': 'test',
                        'confirm_password': 'test',
                        'company': 'IP Ivanov',
                        'position': 'CEO'})
    response = client.post(path='/createuser/',data=data, content_type="application/json")
    assert User.objects.count() == count + 1

    @pytest.mark.django_db
    def test_add_user_upload_data():
        token = Token.objects.get(id=1)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/upload/', {'url': 'http://gw36.a-don.ru:8181/platform/shop1.yaml'})
        client.credentials()
        assert response.status_code == 200
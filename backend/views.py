from pprint import pprint
import urllib.request
import yaml
from yaml import load as load_yaml, Loader
from requests import get
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Shop, Category


class UploadData(APIView):
    def post(self, request):
        url = request.data.get('url')
        stream = get(url).content
        data = yaml.safe_load(stream)
        # pprint(data)
        shop = Shop.objects.get_or_create(name=data['shop'])
        # for category in data['categories']:
        #     cat = Category.objects.get_or_create(id=category['id'], name=category['name'])
        #     cat.shop.add(shop[0].id)
        #     cat.save()
        print(shop.id)

        return Response('Download is ok')



from pprint import pprint
import urllib.request
import yaml
from yaml import load as load_yaml, Loader
from requests import get
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class UploadData(APIView):
    def post(self, request):
        url = request.data.get('url')
        stream = get(url).content
        data = yaml.safe_load(stream)
        # pprint(data)
        shop = Shop.objects.get_or_create(name=data['shop'])
        for category in data['categories']:
            cat = Category.objects.get_or_create(id=category['id'], name=category['name'])
            cat[0].shops.add(shop[0])
            cat[0].save()
        for good in data['goods']:
            category = Category.objects.get(pk=good['category'])
            product = Product.objects.get_or_create(pk=good['id'], name=good['name'], category=category)
            productinfo = ProductInfo.objects.get_or_create(
                product=product[0], shop=shop[0],
                quantity=good['quantity'], price=good['price'],
                price_rrc=good['price_rrc'], model=good['model']
            )
            for parametr, value in good['parameters'].items():
                parametr_name = Parameter.objects.get_or_create(name=parametr)
                ProductParameter.objects.get_or_create(
                    productinfo=productinfo[0],
                    parametr=parametr_name[0],
                    value=value
                )

        return Response('Download is ok')

class CreateUser(APIView):
    def post(self, request):
        passwod = request.data.get('passwod')
        print(passwod)



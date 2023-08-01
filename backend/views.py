from pprint import pprint
import urllib.request
import yaml
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from yaml import load as load_yaml, Loader
from requests import get
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, User, Order, OrderItem
from backend.permissions import IsOwner
from backend.serializers import ProductSerializer, ProductCardSerializer, ProducrInfoSerializer, \
    ProducrInfoShopPriceSerializer, OrderSerializer


class UploadData(APIView):
    """
    Загрузка yaml файла с товарами, файл передается в виде ссылки
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        url = request.data.get('url')
        stream = get(url).content
        data = yaml.safe_load(stream)
        # pprint(data)
        shop = Shop.objects.get_or_create(name=data['shop'], user=request.user)
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
    """
    Создание пользователя
    """
    def post(self, request):
        user = request.data
        confirm_password = user.pop('confirm_password')
        user_check = User.objects.filter(username=user['email'])
        if user_check:
            return Response('User already exist')
        user['username'] = user['email']
        if confirm_password == user['password']:
            user_db = User.objects.create_user(**user)
        else:
            return Response("The password doesn't match")
        token = Token.objects.create(user=user_db)
        return Response(f'User {user["username"]} created, Token: {token}')

class UserEnter(APIView):
    """
    Авторизация пользователя
    """
    def post(self, request):
        data = request.data
        user = authenticate(username=data['email'], password=data['password'])
        if user is None:
            return Response('Email or password is wrong')
        return Response('Login is allowed')

class ProductAPI(ListAPIView):
    """
    Класс для просмотра списка товаров
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(APIView):
    """
    Класс для просмотра карточки товара
    """
    permission_classes = (IsAuthenticated,)
    def get(self, request, id):
        shop = request.GET.get('shop')
        # проверка есть ли фильтр по магазину
        if shop is None:
            product = Product.objects.filter(pk=id)
            ser = ProductCardSerializer(product, many=True)
            return Response(ser.data)
        product_shop = ProductInfo.objects.filter(shop__name=shop, product_id=id)
        ser = ProducrInfoShopPriceSerializer(product_shop, many=True)
        return Response(ser.data)


class OrderViewSet(ModelViewSet):
    """
    Класс для работы с корзиной
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        orderitem = data.pop('orderitem')
        order = Order.objects.create(user=self.request.user, **data)
        OrderItem.objects.create(order=order, **orderitem)
        # print(orderitem)
        return Response('Ok')
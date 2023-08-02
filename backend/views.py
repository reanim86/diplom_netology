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

class OrderViews(APIView):
    """
    Класс для работы с моделью Order
    """
    def get(self, request):
        orders = Order.objects.filter(user=self.request.user)
        ser = OrderSerializer(orders, many=True)
        return Response(ser.data)

    def post(self, request):
        order = Order.objects.create(user=self.request.user)
        return Response(f'Create order with id {order.id}')

    def patch(self, request, id):
        order = Order.objects.get(pk=id)
        if not (order.user == self.request.user):
            return Response('Wrong user')
        data = request.data
        Order.objects.filter(pk=id).update(**data)
        order = Order.objects.get(pk=id)
        ser = OrderSerializer(order)
        return Response(ser.data)




class Basket(ListAPIView):
    """
    Класс для работы с корзиной
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def post(self, request):
        """
        Кладем товар в корзину
        """
        data = request.data
        orderitem = data.pop('orderitem')
        name = orderitem.pop('productinfo')
        productinfos = ProductInfo.objects.filter(product__name=name['name_product'], shop__name=name['name_shop'])
        if productinfos[0].quantity < orderitem['quantity']:
            return Response('There is not enough product on the balance')
        # order = Order.objects.create(user=self.request.user, **data)
        OrderItem.objects.create(order=order, productinfo=productinfos[0], **orderitem)
        # Уменьшаем остаток в магазине на указанное количество товара
        # ProductInfo.objects.filter(product__name=name['name_product'], shop__name=name['name_shop']).update(
        #     quantity=(productinfos[0].quantity - orderitem['quantity'])
        # )
        return Response(f'Product {name["name_product"]}, в количестве {orderitem["quantity"]}, на сумму '
                        f'{(orderitem["quantity"] * productinfos[0].price)} add to basket. Order ID')
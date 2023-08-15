
import yaml
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from requests import get
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, User, Order, OrderItem, \
    Contact
from backend.sendmail import send_email, text_to_admin, text_to_client
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

class ProductAPI(ModelViewSet):
    """
    Класс для просмотра списка товаров
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ['get']

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
    def get(self, request, id):
        orders = Order.objects.filter(pk=id, user=self.request.user)
        orderitems = OrderItem.objects.filter(order=orders[0])
        order_info = []
        full_amount = 0
        user = User.objects.filter(username=self.request.user)
        for orderitem in orderitems:
            productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
            product = Product.objects.get(pk=productinfo.product_id)
            shop = Shop.objects.get(pk=productinfo.shop_id)
            order_info.append(f'Product {product.name} to shop {shop.name} quantity {orderitem.quantity} by price '
                              f'{productinfo.price}, the amount {orderitem.quantity * productinfo.price}')
            full_amount += orderitem.quantity * productinfo.price
        full_info = {'id': orders[0].id, 'date': orders[0].dt,
                     'status': orders[0].status, 'products': order_info,
                     'full_amount': full_amount, 'surname': orders[0].surname,
                     'first_name': user[0].first_name, 'last_name': user[0].last_name,
                     'email':user[0].email}
        return Response(full_info)

    def post(self, request):
        order = Order.objects.create(user=self.request.user)
        return Response(f'Create order with id {order.id}')

    def patch(self, request, id):
        admin_email = 'reanim86@yandex.ru'
        order = Order.objects.get(pk=id)
        user = User.objects.filter(username=self.request.user)
        if order.user != self.request.user:
            return Response('Wrong user')
        data = request.data
        status = data.pop('status')
        # Уменьшаем остаток в магазине на количество товара в заказе если клиент подвердил заказ
        if (status == 'confirmed') and (order.status == 'new'):
            # Создаем или получаем запись контакта куда отправлять заказ
            type_contact = list(data.keys())
            value_contact = list(data.values())
            contact = Contact.objects.get_or_create(
                type=type_contact[0],
                user=self.request.user,
                value=value_contact[0]
            )

            orders = Order.objects.filter(pk=id, user=self.request.user)
            orderitems = OrderItem.objects.filter(order=orders[0])
            for orderitem in orderitems:
                productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
                ProductInfo.objects.filter(pk=orderitem.productinfo_id).update(
                    quantity=(productinfo.quantity - orderitem.quantity)
                )
            text_admin = text_to_admin(
                orderitems,
                contact[0].type,
                contact[0].value,
                user[0].surname,
                user[0].first_name,
                user[0].last_name,
                user[0].email
            )
            send_email(admin_email, f'Accept order {id}', text_admin)
            text_client = text_to_client(
                id,
                orderitems,
                contact[0].type,
                contact[0].value,
                user[0].surname,
                user[0].first_name,
                user[0].last_name,
                user[0].email
            )
            send_email(user[0].email, 'Thank you for your order', text_client)
        # Увеличиваем остаток в магазине если заказ отменен
        if (status == 'canceled') and (order.status != 'new'):
            orders = Order.objects.filter(pk=id, user=self.request.user)
            orderitems = OrderItem.objects.filter(order=orders[0])
            for orderitem in orderitems:
                productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
                ProductInfo.objects.filter(pk=orderitem.productinfo_id).update(
                    quantity=(productinfo.quantity + orderitem.quantity)
                )
        Order.objects.filter(pk=id).update(status=status)
        order = Order.objects.get(pk=id)
        ser = OrderSerializer(order)
        return Response(ser.data)


class Basket(APIView):
    """
    Класс для работы с корзиной
    """
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
        # Проверка что пользователь кладет в свою корзину
        order = Order.objects.get(pk=orderitem["order_id"])
        if order.user != self.request.user:
            return Response("You can't put an item in this basket")
        OrderItem.objects.create(productinfo=productinfos[0], **orderitem)
        return Response(f'Product {name["name_product"]}, в количестве {orderitem["quantity"]}, на сумму '
                        f'{(orderitem["quantity"] * productinfos[0].price)} add to basket. Order ID '
                        f'{orderitem["order_id"]}')

    def delete(self, request, id):
        orderitem = OrderItem.objects.get(pk=id)
        order = Order.objects.get(pk=orderitem.order_id)
        if order.user != self.request.user:
            return Response("You don't have permission")
        orderitem.delete()
        return Response(f'Record with ID {id} delete')

    def patch(self, request, id):
        data = request.data
        orderitem = OrderItem.objects.get(pk=id)
        order = Order.objects.get(pk=orderitem.order_id)
        if order.user != self.request.user:
            return Response("You don't have permission")
        productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
        if productinfo.quantity < data['quantity']:
            return Response('There is not enough product on the balance')
        OrderItem.objects.filter(pk=id).update(quantity=data['quantity'])
        return Response(f'Quantity changed to {data["quantity"]}')
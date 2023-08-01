from rest_framework import serializers

from backend.models import Product, Category, ProductInfo, Shop, Parameter, ProductParameter, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category
    """
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product выводит список товаров
    """
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']

class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Shop
    """
    class Meta:
        model = Shop
        fields = ['name', 'url']

class ParametrSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Parametr
    """
    class Meta:
        model = Parameter
        fields = ['name']

class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductParameter
    """
    parametr = ParametrSerializer(read_only=True)
    class Meta:
        model = ProductParameter
        fields = ['parametr', 'value']

class ProducrInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductInfo
    """
    shop = ShopSerializer(read_only=True)
    productparameters = ProductParameterSerializer(read_only=True, many=True)
    class Meta:
        model = ProductInfo
        fields = ['model', 'price', 'quantity', 'shop', 'productparameters']

class ProductCardSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product выводит характеристики товаров
    """
    productinfos = ProducrInfoSerializer(read_only=True, many=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'productinfos']

class ProducrInfoShopPriceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ProductInfo для вывода остатков и цена по определенному магазину определенного товара
    """
    shop = ShopSerializer(read_only=True)
    productparameters = ProductParameterSerializer(read_only=True, many=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['product', 'model', 'price', 'quantity', 'shop', 'productparameters']

class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order
    """
    class Meta:
        model = Order
        fields = ['user', 'dt', 'status']
        read_only_fields = ['user']

        # def create(self, validated_data):
            # positions = validated_data.pop('positions')
            # order = super().create(validated_data)
            # for position in positions:
            #     StockProduct.objects.create(
            #         stock=stock,
            #         product=position['product'],
            #         quantity=position['quantity'],
            #         price=position['price']
            #     )
            # OrderItem.objects.create(order_id=1, productinfo_id=1, quantity=1)
            # return order

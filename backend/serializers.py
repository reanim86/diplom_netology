from rest_framework import serializers

from backend.models import Product, Category, ProductInfo


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category
    """
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product
    """
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']

class ProducrInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['model', 'price', 'quantity']

class ProductCardSerializer(serializers.ModelSerializer):
    productinfos = ProducrInfoSerializer
    class Meta:
        model = Product
        fields = ['id', 'name', 'productinfos']

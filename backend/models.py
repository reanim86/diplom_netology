import django
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django.db import models




STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование магазина')
    url = models.CharField(max_length=256, null=True, blank=True, verbose_name='Адрес интернет магазина')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Пользователь',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['-name']

    def __str__(self):
        return self.name

class Category(models.Model):

    name = models.CharField(max_length=50, verbose_name='Наименование категории')
    shops = models.ManyToManyField(Shop, related_name='categorys')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-name']

    def __str__(self):
        return self.name

class Parameter(models.Model):

    name = models.CharField(max_length=50, verbose_name='Наименование параметра')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имен параметорв'
        ordering = ['-name']

    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(max_length=50, verbose_name='Наименование продукта')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-name']

    def __str__(self):
        return self.name

class ProductInfo(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productinfos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='productinfos')
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество')
    price = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=19, decimal_places=2, verbose_name='Рекомендованная цена')
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'

class ProductParameter(models.Model):

    productinfo = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='productparameters')
    parametr = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='productparameters')
    value = models.CharField(max_length=50, verbose_name='Значение параметра')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

class User(AbstractUser):
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    surname = models.CharField(max_length=40, null=True, blank=True, verbose_name='Фамилия')

class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=15)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

class Contact(models.Model):

    type = models.CharField(max_length=50, verbose_name='Статус')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    value = models.CharField(max_length=50, verbose_name='Значение')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    productinfo = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.PositiveIntegerField(verbose_name='Количество')






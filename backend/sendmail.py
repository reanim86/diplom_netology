import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.models import ProductInfo, Product, Shop


def send_email(address_to, subject, text_message):
    """
    Функция отпарвляет уведомление по почте
    :param address_to: список адресатов
    :param pass_mail: пароль от почты отпарвления
    """
    text = text_message
    part_text = MIMEText(text, 'plain')

    address_from = 'telreport@a-don.ru'
    msg = MIMEMultipart()
    msg['From'] = address_from
    msg['To'] = address_to
    msg['Subject'] = subject
    msg.attach(part_text)
    server = smtplib.SMTP('smtp.yandex.ru: 587')
    server.starttls()
    server.login(address_from, 'telreport1!Q')
    server.sendmail(address_from, address_to, msg.as_string())
    server.quit()
    return

def text_to_admin(orderitems_arryay, type_contact, value_contact, surname, first_name, last_name, email):
    """
    Формируем текст сообщения для администратора магазина
    """
    order_info = ['Products:']
    full_amount = 0
    text_message = ''
    n = 0
    for orderitem in orderitems_arryay:
        n += 1
        productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
        product = Product.objects.get(pk=productinfo.product_id)
        shop = Shop.objects.get(pk=productinfo.shop_id)
        order_info.append(f'{n}. {product.name}, to shop: {shop.name}, quantity: {orderitem.quantity}, by price: '
                          f'{productinfo.price}, the amount: {orderitem.quantity * productinfo.price};')
        full_amount += orderitem.quantity * productinfo.price
    for text in order_info:
        text_message += text + '\n'
    text_message += f'Full price for order {full_amount}' + '\n'
    text_message += f'Send to {type_contact} {value_contact}' + '\n'
    text_message += f'Contact: {surname} {first_name} {last_name} {email}'
    return text_message

def text_to_client(id_order, orderitems_arryay, type_contact, value_contact, surname, first_name, last_name, email):
    """
    Формируем текст сообщения для клиента (покупателя)
    """
    text_mail = (f'Номер вашего заказа: {id_order}\n'
            f'Наш оператор свяжется с вами в ближайшее время для уточнения делатей заказа\n'
            f'Статуз заказов вы можете посмотреть в разделе "Заказы"\n')
    order_info = ['Products:']
    full_amount = 0
    text_message = ''
    n = 0
    for orderitem in orderitems_arryay:
        n += 1
        productinfo = ProductInfo.objects.get(pk=orderitem.productinfo_id)
        product = Product.objects.get(pk=productinfo.product_id)
        shop = Shop.objects.get(pk=productinfo.shop_id)
        order_info.append(f'{n}. {product.name}, to shop: {shop.name}, quantity: {orderitem.quantity}, by price: '
                          f'{productinfo.price}, the amount: {orderitem.quantity * productinfo.price};')
        full_amount += orderitem.quantity * productinfo.price
    for text in order_info:
        text_message += text + '\n'
    text_message += f'Full price for order {full_amount}' + '\n'
    text_message += f'Send to {type_contact} {value_contact}' + '\n'
    text_message += f'Contact: {surname} {first_name} {last_name} {email}'
    text_mail += text_message
    return text_mail
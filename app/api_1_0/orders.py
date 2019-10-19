from . import api
from .authentication import auth
from flask import g, request, jsonify
from instamojo_wrapper import Instamojo
from os import environ
from app.models import Address, User, Order, OrderProducts, Product
from datetime import datetime
import secrets
import string
im_api = Instamojo(api_key=environ.get('IM_API_KEY'),
                   auth_token=environ.get('IM_AUTH_TOKEN'))

if(environ.get('IM_ENDPOINT')):
    im_api.endpoint = environ.get('IM_ENDPOINT')


def order_id_generator():
    orders = Order.objects.all()
    order_number = int(''.join(secrets.choice(string.digits)
                               for i in range(10)))
    if order_number == next((i for i in orders if i['order_id'] == order_number), False):
        order_id_generator()
    return str(order_number)


@api.route('/user/order/new', methods=['POST'])
@auth.login_required
def create_order():
    user = User.objects.get(email=g.current_user['email'])
    request_data = request.json

    order_total = request_data['total']
    send_email = request_data['send_email']
    order_discount = request_data['total_discount']
    order_tax = request_data['estimated_tax']
    delivery_address = request_data['delivery_address']
    billing_address = request_data['billing_address']
    payment_mode = request_data['payment_mode']

    email = user.email
    phone = user.contact_number
    buyer_name = user.name

    order = Order()
    order.order_id = order_id_generator()
    if payment_mode == 'online':
        im_response = im_api.payment_request_create(
            amount=order_total,
            purpose=order.order_id,
            send_email=send_email,
            email=email,
            buyer_name=buyer_name,
            phone=phone,
            redirect_url=str(environ.get('FRONTEND_BASE_URL')) + 'order-placed')

        payment_request_url = im_response['payment_request']['longurl']
        payment_request_id = im_response['payment_request']['id']
    if payment_mode == 'COD':
        payment_request_url = None
        payment_request_id = None
        order.payment_status = 'success'

    order.user = user
    order.tax = order_tax
    order.discount = order_discount
    order.total = order_total
    delivery_add = Address(
        address=delivery_address['address'], zip_code=delivery_address['zip_code'], city=delivery_address['city'])
    order.delivery_address = delivery_add
    billing_add = Address(
        address=billing_address['address'], zip_code=billing_address['zip_code'], city=billing_address['city'])
    order.billing_address = billing_add
    order.status_log.update({'v' + str(len(order.status_log) + 1):
                             {'date': datetime.utcnow(),
                              'status': order.status}})
    order.payment_mode = payment_mode
    order.payment_request_id = payment_request_id
    order.products = []
    for item in user.cart:
        product = Product.objects.get(code=item['code'])
        op = OrderProducts()
        op.name = product.name
        op.description = product.description
        op.specifications = product.specifications
        op.images = product.images
        op.code = product.code
        op.quantity = item['quantity']
        op.warranty = product.warranty
        op.warranty_expiry = op.warranty_date_setter()
        op.condition = product.condition
        op.price = product.price
        op.discount_percentage = product.discount_percentage
        op.category = product.category
        order.products.append(op)

    order.save()
    user.cart = []
    user.save()

    return jsonify({'status': 'success', 'payment_mode': payment_mode, 'payment_requet_url': payment_request_url, 'order_id': order.order_id}), 201


@api.route('/user/order/update', methods=['POST'])
@auth.login_required
def update_order():
    request_data = request.json
    payment_id = request_data['payment_id']
    payment_status = request_data['payment_status']
    payment_request_id = request_data['payment_request_id']
    order = Order.objects.get(payment_request_id=payment_request_id)

    if payment_status == 'Credit':
        order.payment_id = payment_id
        order.save()

    return jsonify({'status': 'order updated', 'order': order}), 200


@api.route('/user/order', methods=['GET'])
@auth.login_required
def get_orders():
    user = User.objects.get(email=g.current_user['email'])
    orders = Order.objects.filter(user=user)
    return jsonify({'orders': orders}), 200


@api.route('/user/order/<order_id>', methods=['GET'])
@auth.login_required
def get_order(order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        return jsonify({'order': order}), 200
    except:
        return jsonify({'status': 'invalid order id'}), 400

@api.route('/user/order/payment_request_id/<payment_request_id>', methods=['GET'])
@auth.login_required
def get_order_payment_request(payment_request_id):
    try:
        order = Order.objects.get(payment_request_id=payment_request_id)
        return jsonify({'order': order}), 200
    except:
        return jsonify({'status': 'invalid payment request id'}), 400

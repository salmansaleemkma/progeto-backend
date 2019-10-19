from app.models import User
from flask import jsonify, request, abort, g
from . import api
from .authentication import auth
from mongoengine import DoesNotExist
from sendgrid.helpers.mail import Email, Mail, Personalization
from os import environ
import sendgrid
import urllib
import json
import secrets
import string
sg = sendgrid.SendGridAPIClient(apikey=environ.get('SENDGRID_API_KEY'))


@api.route('/user/<username>', methods=['GET', 'POST'])
def user(username):

    try:
        if User.objects.get(email=username) is not None:
            return jsonify({'success': 'User exists'}), 200
    except DoesNotExist:
        return jsonify({'error': 'username not found'}), 400

    return jsonify({'error': 'username not found'}), 400


@api.route('/user/profile', methods=['GET'])
@auth.login_required
def user_profile():

    user = User.objects.exclude('referrals_list', 'signup_timestamp',
                                'login_log', 'password_hash').get(email=g.current_user.email)
    return jsonify({'user': user}), 200


@api.route('/user/cart', methods=['GET', 'POST'])
@auth.login_required
def user_cart():
    user = User.objects.get(email=g.current_user.email)
    if request.method == 'POST':
        request_data = request.json
        product = request_data['product']
        try:
            itemIndex = user.cart.index(
                next(i for i in user.cart if i['code'] == product['code']))
            if(itemIndex):
                user.cart[itemIndex]['quantity'] += product['quantity']
                user.save()

        except StopIteration:
            user.cart.append(product)
            user.save()

        return jsonify({'status': 'cart updated', 'cart': user.cart}), 201
    return jsonify({'cart': user.cart}), 200


@api.route('/user/cart/remove', methods=['POST'])
@auth.login_required
def remove_from_cart():
    user = User.objects.get(email=g.current_user.email)
    if request.method == 'POST':
        request_data = request.json
        for item in user.cart:
            if item['code'] == request_data['code']:
                index = user.cart.index(item)
                user.cart.pop(index)

        user.save()
        return jsonify({'cart': user.cart}), 201


@api.route('/user/account/register', methods=['POST'])
def new_user():
    request_data = request.json
    name = request_data['name']
    email = request_data['email']
    password = request_data['password']

    if email is None or password is None:
        abort(400)  # missing arguments
    try:
        if User.objects.get(email=email) is not None:
            return jsonify({'error': 'User already exists'}), 400
    except DoesNotExist:
        user = User(email=email)
        user.password = password
        user.email = email
        user.name = name
        user.save()

        token = user.generate_confirm_token()
        from_email = Email("no-reply@progeto.in")
        subject = None
        mail = Mail(from_email, subject)
        p = Personalization()
        tokenlink = environ.get('FRONTEND_BASE_URL') + \
            'confirm-account/' + token
        p.dynamic_template_data = {'tokenlink': tokenlink}
        p.add_to(Email(user.email))
        mail.add_personalization(p)
        mail.template_id = environ.get('CONFIRM_TEMPLATE_ID')
        response = sg.client.mail.send.post(request_body=mail.get())

    return jsonify({'user': user.email, 'confirm_email_status': response.status_code}), 201


@api.route('/user/account/confirm/<token>', methods=['GET', 'POST'])
def confirm_user(token):
    users = User.objects.all()
    for user in users:
        if user.confirm(token):
            return jsonify({'status': 'account confirmed'}), 200

    return jsonify({'status': 'invalid token'}), 400


@api.route('/user/account/login', methods=['POST'])
def user_login():
    request_data = request.json
    if request_data:
        username = request_data['username']
        password = request_data['password']

    if username != '':
        try:
            user = User.objects.get(email=username)
            if not user.verify_password(password):
                return jsonify({'error': 'incorrect password'}), 401
            return jsonify({'token': user.generate_auth_token()}), 200
        except DoesNotExist:
            return jsonify({'error': 'user does not exist'}), 401

    return jsonify({'error': 'invalid request'}), 400


@api.route('/user/account/password/reset/<email>', methods=['GET', 'POST'])
def password_reset_link(email):
    try:
        user = User.objects.get(email=email)
        if user:
            token = user.generate_confirm_token()
            from_email = Email("no-reply@progeto.in")
            subject = None
            mail = Mail(from_email, subject)
            p = Personalization()
            resetlink = environ.get('FRONTEND_BASE_URL') + \
                'reset-password/' + token
            p.dynamic_template_data = {'resetlink': resetlink}
            p.add_to(Email(user.email))
            mail.add_personalization(p)
            print(mail.get())
            mail.template_id = environ.get('RESET_TEMPLATE_ID')
            response = sg.client.mail.send.post(request_body=mail.get())

            return jsonify({'status': 'reset password email sent'}), 201
    except DoesNotExist:
        return jsonify({'status': 'invalid email address'}), 400


@api.route('/user/account/password/token', methods=['POST'])
def user_password_reset():

    request_data = request.json
    token = request_data['token']
    password = request_data['password']

    users = User.objects.all()
    for user in users:
        if user.confirm(token):
            user.password = password
            user.save()

            return jsonify({'status': 'password reset successfully'}), 201

    return jsonify({'status': 'password reset failed'}), 400


@api.route('/user/phone/otp/send', methods=['POST'])
@auth.login_required
def send_otp_sms():
    request_data = request.json
    numbers = '91' + str(request_data['phone'])

    user = User.objects.get(email=g.current_user['email'])
    user.contact_number = request_data['phone']
    otp = int(''.join(secrets.choice(string.digits)
                      for i in range(6)))
    user.conf_otp = otp
    user.save()
    message = 'Hello from Progeto, your OTP is ' + str(otp)
    data = urllib.parse.urlencode({'apikey': environ.get(
        'TXTLCL_API_KEY'), 'numbers': numbers, 'message': message, 'sender': 'TXTLCL'})
    data = data.encode('utf-8')
    txt_request = urllib.request.Request("https://api.textlocal.in/send/")
    get_response = urllib.request.urlopen(txt_request, data)
    txt_response = json.loads(get_response.read().decode('utf-8'))

    if txt_response['status'] == 'success':
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': txt_response['status'], 'errors': txt_response['errors']}), 400


@api.route('/user/phone/otp/verify', methods=['POST'])
@auth.login_required
def verify_otp():
    request_data = request.json
    code = int(request_data['code'])
    user = User.objects.get(email=g.current_user['email'])

    if code == user.conf_otp:
        user.contact_verified = True
        user.save()
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'Invalid OTP. please try again.'}), 400

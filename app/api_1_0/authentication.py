from flask_httpauth import HTTPBasicAuth
from app.models import User
from flask import g, jsonify
from . import api
from mongoengine import DoesNotExist
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    user = User.verify_auth_token(email_or_token)

    if not user:
        try:
            user = User.objects.get(email=email_or_token)
            if not user.verify_password(password):
                return False
        except DoesNotExist:
            return False

    g.current_user = user
    g.token_used = True

    return True


@api.route('/token/')
@auth.login_required
def get_token():

    if g.token_used:
        return jsonify({'token': str(g.current_user.generate_auth_token(expiration=18000)), 'expiration': 18000})

    else:
        return forbidden('Unauthorized access')

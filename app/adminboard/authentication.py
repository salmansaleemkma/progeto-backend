from . import adminboard
from app.models import AdminUser
from functools import wraps
from mongoengine import DoesNotExist
from flask import session, flash, redirect, url_for, request, render_template


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session:
            return redirect(url_for('adminboard.login'))
        return f(*args, **kwargs)
    return decorated_function


@adminboard.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username != '':
            try:
                user = AdminUser.objects.get(email=username)
                if not user.verify_password(password):
                    flash('Incorrect password')
                    return render_template('login.html'), 401
                session['username'] = user.email
                return redirect(url_for('adminboard.index'))
            except DoesNotExist:
                flash('Invalid username')

    return render_template('login.html'), 200


@adminboard.route('/logout/')
def logout():
    session.pop('username', None)
    flash('You are logged out')
    return redirect(url_for('adminboard.login'))

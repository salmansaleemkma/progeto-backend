from .authentication import login_required
from . import adminboard
from app.models import User, Order
from flask import render_template, jsonify, request, flash
from mongoengine import errors, queryset
from uuid import UUID


@adminboard.route('/customers/', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        query = request.form['query']
        if query != '':
            users = User.objects.search_text(query)
            return render_template('customers.html', customers=users)
    users = User.objects.all()
    return render_template('customers.html', customers=users)


@adminboard.route('/customers/<customer_id>/', methods=['GET', 'POST'])
@login_required
def get_customer(customer_id):
    try:
        customer = User.objects.exclude(password_hash).get(id=UUID(customer_id))
        orders = Order.objects.get(user=customer)
        print(customer)
        # if not isinstance(orders, queryset.queryset.QuerySet):
        #     orders = [orders]
        return render_template('customer_page.html', customer=customer, orders=orders)
    except:
        pass

    return render_template('customer_page.html', customer=None, orders=None), 401

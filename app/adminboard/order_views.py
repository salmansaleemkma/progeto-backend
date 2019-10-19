from . import adminboard
from .authentication import login_required
from flask import render_template, request, flash
from app.models import Order, OrderStates


@adminboard.route('/orders/', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        query = request.form['query']
        if query != '':
            orders = Order.objects.search_text(query)
            return render_template('orders.html', orders=orders)
    orders = Order.objects.all()
    return render_template('orders.html', orders=orders)


@adminboard.route('/orders/<order_id>/', methods=['GET', 'POST'])
@login_required
def get_order(order_id):

    order = Order.objects.get(order_id=order_id)

    if request.method == 'POST':
        data = request.form
        print(data['status'])
        order.status = data['status']
        order.save()
        flash('Status Update successful.')

    return render_template('order_page.html', order=order, orderstates=OrderStates)

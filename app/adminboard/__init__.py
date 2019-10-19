from flask import Blueprint

adminboard = Blueprint('adminboard', __name__, template_folder='templates')

from . import product_views, order_views, customer_views, dashboard_views, \
    errors, authentication, setup_views

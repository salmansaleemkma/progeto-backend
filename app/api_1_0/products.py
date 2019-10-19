from . import api
from app.models import Product, ProductCategory
from flask import jsonify, send_file, request
from mongoengine import errors
import os

PRODUCT_IMAGE_FOLDER = os.getcwd() + '/app/static/product-images/'


@api.route('/products/', methods=['GET'])
def products():
    products = []
    products_raw = Product.objects.all().exclude(
        'images.product_image').exclude('units')
    for product in products_raw:
        if product.archive == False:
            products.append(product)
    return jsonify({'products': products}), 200


@api.route('/products/<product_code>', methods=['GET'])
def get_product(product_code):
    try:
        product = Product.objects.exclude(
            'images.product_image').exclude('units').get(code=product_code)
        if product:
            return jsonify(product), 200
        if product.archive:
            return jsonify({'result': 'product has been archieved'}), 200

    except errors.DoesNotExist:
        return jsonify({'error': 'Product not found.'}), 404
    return jsonify({'error': 'Product not found.'}), 404


@api.route('/products/images/<product_code>/<file_name>/', methods=['GET'])
def product_image(product_code, file_name):

    filepath = os.path.join(PRODUCT_IMAGE_FOLDER, file_name)
    if os.path.exists(filepath):
        return send_file(filepath, attachment_filename=file_name)

    product = Product.objects.get(code=product_code)
    for image_file in product.images:
        if image_file.image_name == file_name:
            f = open(filepath, 'wb')
            f.write(image_file.product_image.read())
            f.close()
            return send_file(filepath, attachment_filename=file_name)
    return 'File Does not Exist', 404


@api.route('/products/category/<category>', methods=['GET'])
def product_category(category):

    product_category = category.replace("-", " ").title()

    if product_category in ProductCategory:

        products = Product.objects.filter(
            category=product_category).all().exclude('images.product_image')

        return jsonify({'products': products}), 200

    return jsonify({'error': 'Unknown Category'}), 404


@api.route('/products/search/<query>', methods=['GET', 'POST'])
def product_search(query):

    if query != '':
        products = Product.objects.exclude('units').exclude(
            'minimum_discounted_price').exclude('images.product_image').search_text(query)

        return jsonify({'products': products})

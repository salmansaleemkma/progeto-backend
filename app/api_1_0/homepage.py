from . import api
from app.models import Carousel, Product
import os
from flask import jsonify, send_file

CAROUSEL_IMAGE_FOLDER = os.getcwd() + '/app/static/carousel-images/'


@api.route('/homepage/carousel-images/', methods=['GET'])
def carousel_images():
    carousels = Carousel.objects.all().exclude('image')
    return jsonify({'carousels': carousels}), 200


@api.route('/homepage/carousel-images/<file_name>/', methods=['GET'])
def get_carousel_image(file_name):

    filepath = os.path.join(CAROUSEL_IMAGE_FOLDER, file_name)
    if os.path.exists(filepath):
        return send_file(filepath, attachment_filename=file_name)

    carousels = Carousel.objects.all()
    for carousel in carousels:
        if carousel.file_name == file_name:
            f = open(filepath, 'wb')
            f.write(carousel.image.read())
            f.close()
            return send_file(filepath, attachment_filename=file_name)
    return 'File Does not Exist', 404

@api.route('/homepage/bestdeals/', methods=['GET'])
def best_deals():
    products = Product.objects(discount_percentage__gt=0).exclude('images').exclude('units')
    bestDeals = []
    for product in products:
        bestDeals.append(product.code)

    return jsonify({'deals': bestDeals }), 200

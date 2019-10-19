import os
from . import adminboard
from .authentication import login_required
from mongoengine import DoesNotExist, errors
from app.models import Product, ProductImage
from app.models import AdminUser, ProductCategory, ProductConditions
from flask import render_template, url_for, request, redirect, \
    flash, jsonify, send_file
from random import randint

PRODUCT_IMAGE_FOLDER = os.getcwd() + '/app/static/product-images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@adminboard.route('/products/', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        query = request.form['query']
        if query != '':
            products = Product.objects.search_text(query)
            return render_template('products.html', products=products)

    products = Product.objects.all()
    return render_template('products.html', products=products)


@adminboard.route('/products/<product_code>/', methods=['GET'])
@login_required
def get_product(product_code):
    randomNumber = str(randint(100, 10000))
    try:
        product = Product.objects.get(code=product_code)
        return render_template('product_page.html', product=product, randomNumber=randomNumber)

        if product_code is None:
            flash('Invalid product code')
            return render_template('product_page.html', product=product)

    except DoesNotExist:
        flash('Product not found')
        return render_template('product_page.html', product=None), 404


@adminboard.route('/products/images/<product_code>/<file_name>/', methods=['GET'])
@login_required
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


@adminboard.route('/products/images/edit/<product_code>/<file_name>', methods=['GET', 'POST'])
@login_required
def edit_product_image(product_code, file_name):

    product = Product.objects.get(code=product_code)
    randomNumber = str(randint(100, 10000))

    if request.method == 'POST':
        data = request.form
        filepath = os.path.join(PRODUCT_IMAGE_FOLDER, file_name)
        if os.path.exists(filepath):
            os.remove(filepath)

        file = request.files['file']
        if file and allowed_file(file.filename):
            file.save(filepath)

        for image in product.images:
            if image.image_name == file_name:
                i = product.images.index(image)

        f = open(filepath, 'rb')
        product.images[i].product_image.replace(f)

        product.save()
        flash('Product image updated.')
        return redirect(url_for('adminboard.edit_product_image', product_code=product_code, file_name=file_name, randomNumber=randomNumber))

    return render_template('view_or_update_product_image.html', product_code=product_code, file_name=file_name, randomNumber=randomNumber)


@adminboard.route('/products/new_product_form/', methods=['GET', 'POST'])
@login_required
def new_product():

    if request.method == 'POST':
        try:
            data = request.form
            new_product = Product()
            new_product.code = data['product_code']
            i = 1
            for img_file in request.files:
                file = request.files[img_file]
                if file and allowed_file(file.filename):

                    filename = new_product.code + '-' + str(i) + '.jpg'
                    filepath = PRODUCT_IMAGE_FOLDER + filename
                    file.save(os.path.join(PRODUCT_IMAGE_FOLDER, filename))

                    db_image = ProductImage()
                    db_image.image_name = filename
                    db_image.product_image.put(filepath)

                    i = i + 1
                    new_product.images.append(db_image)

            new_product.description = data['description']
            new_product.name = data['name']
            new_product.category = data['category']
            new_product.condition = data['condition']
            new_product.price = float(data['price'])
            new_product.mrp = float(data['mrp'])
            new_product.warranty = data['warranty']
            new_product.units = data['units']
            new_product.minimum_discounted_price = float(
                data['minimum_discounted_price'])
            new_product.discount_percentage = data['discount_percentage']
            new_product.specifications = {}
            new_product.specifications['capacity'] = data['capacity']
            new_product.specifications['dimensions'] = data['dimensions']
            new_product.specifications['model'] = data['model']
            new_product.specifications['sub_category'] = data['sub_category']
            new_product.specifications['accessories'] = data['accessories']
            new_product.specifications['brand'] = data['brand']

            if int(new_product.units) > 0:
                new_product.instock = True
            new_product.save()
            flash('new product added')
            return redirect(url_for('adminboard.get_product', product_code=new_product.code))
        except ValueError:
            flash('Please make sure all fields are entered correctly')
        except errors.ValidationError:
            flash('Invalid input')
        except errors.NotUniqueError:
            flash('Error: Product code already used. Please use a unique product code.')
    return render_template('new_product.html', category_list=ProductCategory,
                           condition_list=ProductConditions)


@adminboard.route('/products/edit/<product_code>/', methods=['GET', 'POST'])
@login_required
def edit_product(product_code):
    product = Product.objects.get(code=product_code)

    if request.method == 'POST':
        try:
            data = request.form

            product.description = data['description']
            product.name = data['name']
            product.category = data['category']
            product.condition = data['condition']
            product.price = float(data['price'])
            product.mrp = float(data['mrp'])
            product.warranty = data['warranty']
            product.minimum_discounted_price = float(data['minimum_discounted_price'])
            product.discount_percentage = data['discount_percentage']
            product.units = data['units']
            # if product.specifications is None:
            #     product.specifications = {}
            product.specifications['capacity'] = data['capacity']
            print(product.specifications['capacity'])
            product.specifications['dimensions'] = data['dimensions']
            product.specifications['model'] = data['model']
            product.specifications['sub_category'] = data['sub_category']
            product.specifications['accessories'] = data['accessories']
            product.specifications['brand'] = data['brand']
            if int(product.units) > 0:
                product.instock = True
            else:
                product.instock = False
            product.save()
            flash('Product Details Updated')
            return redirect(url_for('adminboard.get_product', product_code=product.code))
        except ValueError or errors.ValidationError:
            flash('Invalid input')

    return render_template('edit_product.html', product=product,
                           category_list=ProductCategory,
                           condition_list=ProductConditions)

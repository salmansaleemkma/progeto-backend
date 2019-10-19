from . import adminboard
from flask import jsonify, session, render_template, send_file, request, flash, redirect, url_for
from .authentication import login_required
from app.models import Carousel
import os
from mongoengine import errors
from random import randint

CAROUSEL_IMAGE_FOLDER = os.getcwd() + '/app/static/carousel-images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@adminboard.route('/setup/', methods=['GET'])
@login_required
def homepage_setup():
    carousels = Carousel.objects.all()
    carouselCount = len(carousels)
    randomNumber = str(randint(100, 10000))
    return render_template('homepage_setup.html', carousels=carousels, carouselCount=carouselCount, randomNumber=randomNumber)


@adminboard.route('/homepage/carousels/new', methods=['GET', 'POST'])
@login_required
def add_new_carousel():
    carousels = Carousel.objects.all()
    carouselCount = len(carousels) + 1
    filename = 'carousel-' + str(carouselCount) + '.png'
    if request.method == 'POST':
        try:
            carousel = Carousel()
            data = request.form
            filepath = os.path.join(CAROUSEL_IMAGE_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            carousel.file_name = filename
            file = request.files['file']
            if file and allowed_file(file.filename):

                filepath = CAROUSEL_IMAGE_FOLDER + filename
                file.save(filepath)
                f = open(filepath, 'rb')
                carousel.image.put(f)

            carousel.save()
            flash('Carousel Added')
            return redirect(url_for('adminboard.homepage_setup', file_name=carousel.file_name))
        except ValueError or errors.ValidationError:
            flash('Invalid input')
        except errors.NotUniqueError:
            flash(
                'another carousel with this file name exists, please try with a different name.')
    return render_template('add_new_carousel.html')


@adminboard.route('/homepage/carousels/<file_name>/', methods=['GET'])
@login_required
def get_carousel_image(file_name):
    filepath = os.path.join(CAROUSEL_IMAGE_FOLDER, file_name)
    if os.path.exists(filepath):
        return send_file(filepath, attachment_filename=file_name)

    carousels = Carousel.objects.all()
    for carousel in carousels:
        if carousel.file_name == file_name:
            f = open(filepath, 'wb+')
            f.write(carousel.image.read())
            f.close()
            return send_file(filepath, attachment_filename=file_name)
    return 'File Does not Exist', 404


@adminboard.route('/homepage/carousels/view/<file_name>', methods=['GET', 'POST'])
@login_required
def view_or_update_carousel(file_name):
    carousel = Carousel.objects.get(file_name=file_name)
    randomNumber = str(randint(100, 10000))

    if request.method == 'POST':
        try:
            data = request.form
            filepath = os.path.join(CAROUSEL_IMAGE_FOLDER, file_name)
            if os.path.exists(filepath):
                os.remove(filepath)

            file = request.files['file']
            if file and allowed_file(file.filename):

                filepath = CAROUSEL_IMAGE_FOLDER + carousel.file_name
                file.save(filepath)
                f = open(filepath, 'rb')
                carousel.image.replace(f)

            carousel.save()
            flash('Carousel Details Updated')
            return redirect(url_for('adminboard.view_or_update_carousel', file_name=carousel.file_name))
        except ValueError or errors.ValidationError:
            flash('Invalid input')
        except errors.NotUniqueError:
            flash(
                'another carousel with this file name exists, please try with a different name.')

    return render_template('view_or_update_carousel.html', carousel=carousel, randomNumber=randomNumber)

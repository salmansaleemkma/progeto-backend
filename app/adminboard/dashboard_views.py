from . import adminboard
from flask import jsonify, session, render_template
from .authentication import login_required


@adminboard.route('/', methods=['GET'])
@login_required
def index():
    adminuser = session['username']
    return render_template('index.html', adminuser=adminuser)

from functools import wraps

from flask import Flask, render_template, send_file, flash, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from chars import *

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    regions = set([r[0] for r in CITIES])
    return render_template('index.html', regions=regions)


@app.route('/region/<string:region>')
def region(region):
    """Views for the city details"""

    cities = [r[1] for r in CITIES if r[0] == region]
    return render_template('region.html', region=region, cities=cities)


@app.route('/region<string:region>.png')
def region_plot(region):
    """Views for rendering city specific charts"""
    img = get_region_image(region)
    return send_file(img, mimetype='image/png', cache_timeout=0,)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/main.png')
def main_plot():
    img = get_main_image()
    return send_file(img, mimetype='image/png', cache_timeout=0)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/login/<string:region>', methods=["GET", "POST"])
def login(region):
    """The view for the login page"""
    try:
        error = ''
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            user_found = users.filter_by(username=attempted_username, region=region).first()
            password = user_found.password
            print('input={},db={}'.format(attempted_password, password))
            if attempted_password == password:
                session['logged_in'] = True
                session['username'] = user_found.username
                return redirect(url_for('edit_database', region=region))
            else:
                print('invalid credentials')
                error = 'Invalid credentials. Please, try again.'
        return render_template('login.html', error=error, region=region)
    except Exception as e:
        return render_template('login.html', error=str(e), region=region)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        """login session"""
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            pass
        return redirect(url_for('login'))

    return wrap


# To use session, you must do the following:
app.secret_key = os.environ['FLASK_WEB_APP_KEY']


@app.route('/edit/<string:region>', methods=["GET", "POST"])
@login_required
def edit_database(region):
    """Views for editing city specific data"""
    records = [(get_loss_times(r), get_place(r)[1], get_cunlan(r), get_loss(r), get_damage(r)) for r in data.filter_by(region=region)]

    try:
        if request.method == "POST":
            for i in range(len(records)):
                damagestartdate = request.form[f'damagestartdate{i}']
                damagestartplace = request.form[f'damagestartplace{i}']
                cunlan = int(request.form[f'cunlan{i}'])
                items = int(request.form[f'items{i}'])
                damage_items = int(request.form[f'damage_items{i}'])
                it = data.filter_by(damagestartdate=damagestartdate, damagestartplace=damagestartplace).first()
                if it:
                    it.cunlan = cunlan
                    it.items = items
                    it.damage_items = damage_items
                else:
                    pass
                #db_session.execute(PigIll.__table__.insert(), self.dicts)

            db_session.commit()
            return redirect(url_for('region', region=region))
        else:
            return render_template('edit.html', region=region, records=records)
    except Exception as error:
        db_session.rollback()
        return render_template('edit.html', region=region, records=records, error=error)



if __name__ == '__main__':
    app.run()

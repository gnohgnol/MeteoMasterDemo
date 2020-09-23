from functools import wraps

from flask import Flask, render_template, send_file, flash, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from chars import *
from jinja2 import Environment, PackageLoader
import datetime
import dotenv
from login_form import LoginForm
from register_form import *



def dateformat(value, format="%Y-%m"):
    return value.strftime(format)

#env=Environment(loader=PackageLoader('app','templates'))
#env.filters['dateformat'] = dateformat


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md', 'wps'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.filters['dateformat'] = dateformat


@app.route('/', methods=['GET', 'POST'])
def index():
    regions = set([r[0] for r in CITIES])
    return render_template('index.html', regions=regions)


@app.route('/region/<string:region>', methods=['GET', 'POST'])
def region(region):
    """Views for the city details"""

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
            os.makedirs(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], region)), exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], region, filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            doc = Document(
                publish_datetime = datetime.datetime.now(),
                filePath = filename,
                region=region)
            db_session.add(doc)
            db_session.commit()

    cities = [r[1] for r in CITIES if r[0] == region]
    docs = db_session.query(Document).filter_by(region=region)
    return render_template('region.html', region=region, cities=cities, docs=docs)


@app.route('/region<string:region>.png')
def region_plot(region):
    """Views for rendering city specific charts"""
    img = get_region_image(region)
    return send_file(img, mimetype='image/png', cache_timeout=0,)


@app.route('/uploads/<string:filename>')
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
        form = LoginForm(request.form)
        if request.method == "POST" and form.validate():
            attempted_username = form.username.data
            attempted_password = form.password.data
            user_found = users.filter_by(username=attempted_username, region=region).first()
            password = user_found.password
            if attempted_password == password:
                session['logged_in'] = True
                session['username'] = user_found.username
                session['icon'] = user_found.iconPath
                return redirect(url_for('edit_database', region=region))
            else:
                print('invalid credentials')
                error = 'Invalid credentials. Please, try again.'
        return render_template('login.html', error=error, region=region, form=form)
    except Exception as e:
        return render_template('login.html', error=str(e), region=region, form=form)


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
    #print(len(records))
    #print('method={}'.format(request.method))
    try:
        if request.method == "POST":
            for i in range(len(records)):
                damagestartdate = request.form[f'damagestartdate{i}']
                damagestartplace = request.form[f'damagestartplace{i}']
                cunlan = request.form[f'cunlan{i}']
                items = request.form[f'items{i}']
                damage_items = request.form[f'damage_items{i}']
                print('date: {} place: {} cunlan: {} items: {} damage_items: {}'.format(damagestartdate, damagestartplace, cunlan, items, damage_items))
                it = data.filter_by(damagestartdate=damagestartdate, damagestartplace=damagestartplace).first()
                if it:
                    it.cunlan = cunlan if cunlan != 'None' else None
                    it.items = items if items != 'None' else None
                    it.damage_items = damage_items if damage_items != 'None' else None
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


@app.route('/add/<string:region>', methods=["GET", "POST"])
@login_required
def edit_database_add(region):
    print(session['username'],session['logged_in'])
    try:
        if request.method == 'POST':
            print('method={}'.format(request.method))
            r = PigIll(
                damagestartdate = (datetime.datetime.strptime(request.form['damagestartdate'], '%Y-%m-%d')-datetime.datetime(1900,1,1)).days+1,
                damagestartplace = request.form['damagestartplace'],
                cunlan = int(request.form['cunlan']),
                items = int(request.form['items']),
                damage_items = int(request.form['damage_items']),
                region = region)
            print(r.damagestartdate, r.damagestartplace, r.cunlan, r.items, r.damage_items, r.region)
            db_session.add(r)
            db_session.commit()
            return redirect(url_for('edit_database', region=region))
        else:
            return render_template('add.html', region=region)
    except Exception as error:
        print(error)
        db_session.rollback()
        return render_template('add.html', region=region)


# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    #if request.method == 'POST' and form.validate():
    if request.method == 'POST':
        region = form.region.data
        file = request.files['icon']
        #print('{}'.format(file))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            iconPath = filename
            file.save( os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file', filename=filename))
        user = User(username=form.username.data,
                    password=form.password.data,
                    region=region,
                    iconPath=iconPath)
        db_session.add(user)
        db_session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login', region=region))
    else:
        return render_template('register.html', form=form)



if __name__ == '__main__':
    app.run()

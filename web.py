from flask import Flask, render_template, url_for, flash, redirect
from flask import session, g, after_this_request, request
from forms import RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from audio import printWAV
import time
import random
import threading
from turbo_flask import Turbo
from flask_behind_proxy import FlaskBehindProxy

# this gets the name of the file so Flask knows it's name
app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = 'c3eec5c8ffb8f4c3b45f24e2b11bf875'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


interval = 20
FILE_NAME = "TTC.wav"
turbo = Turbo(app)


# this tells you the URL the method below is related to
@app.route("/")
def home():
    return render_template('home.html', subtitle='Home Page',
                           text='This is the home page')


@app.route("/about")
def about():
    return render_template('about.html', subtitle='About Page',
                           text='This is the about page')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # checks if entries are valid
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/captions")
def captions():
    TITLE = "HOW SCHOOL MAKES KIDS LESS INTELLIGENT | EDDY ZHONG"
    return render_template('captions.html', songName=TITLE, file=FILE_NAME)


@app.before_first_request
def before_first_request():
    # resetting time stamp file to 0
    try:
        file = open("pos.txt", "w")
    except fileOpenException:
        print("pos.txt could no be opened")
    else:
        file.write(str(0))
    finally:
        file.close()

    # starting thread that will time updates
    threading.Thread(target=update_captions, daemon=True).start()


@app.context_processor
def inject_load():
    # getting previous time stamp
    try:
        file = open("pos.txt", "r")
    except fileOpenException:
        print("pos.txt could no be opened")
    else:
        pos = int(file.read())
    finally:
        file.close()
    # writing next time stamp
    try:
        file = open("pos.txt", "w")
    except fileOpenException:
        print("pos.txt could no be opened")
    else:
        file.write(str(pos+interval))
    finally:
        file.close()

    # returning captions
    return {'caption': printWAV(FILE_NAME, pos=pos, clip=interval)}


def update_captions():
    with app.app_context():
        while True:
            # timing thread waiting for the interval
            time.sleep(interval)
            # forcefully updating captionsPane with caption
            turbo.push(turbo.replace(render_template('captionsPane.html'),
                                     'load'))


if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0", use_reloader=False)

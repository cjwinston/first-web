from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)                    # this gets the name of the file so Flask knows it's name
app.config['SECRET_KEY'] = 'c3eec5c8ffb8f4c3b45f24e2b11bf875'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

@app.route("/")                          # this tells you the URL the method below is related to
def home():
    return render_template('home.html', subtitle='Home Page', text='This is the home page')

@app.route("/about")
def about():
    return render_template('about.html', subtitle='About Page', text='This is the about page')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
    return render_template('register.html', title='Register', form=form)

@app.route("/captions")
def captions():
    TITLE = "Tyler, The Creator - I THOUGHT YOU WANTED TO DANCE (ft. Fana Hues)"
    FILE_NAME = "TTC.wav"
    return render_template('captions.html', songName=TITLE, file=FILE_NAME)

if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")

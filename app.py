from flask import Flask, flash, redirect, render_template, request, session, abort
 

import os
import urlparse
import psycopg2

app = Flask(__name__)

url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
schema = "schema.sql"
conn = psycopg2.connect(db)

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://mbgugkwmyyrgpp:08f1f171ba8df81468de5e7d166069757cc545fb163d5cc820407068513b101d@ec2-54-163-237-249.compute-1.amazonaws.com:5432/da0io40vrbg6u0"
# db = SQLAlchemy(app)
# conn = psycopg2.connect(db)
# cur = conn.cursor()
# app = Flask(__name__)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login.html')
def returningUser():
    return render_template('login.html')

@app.route('/home.html')
def login():
    return render_template('home.html')
def guest():
    # should look different than a registered user (not able to add, delete, etc)
    return render_template('home.html')

@app.route('/register.html')
def newUser():
    return render_template('register.html')
def register():
    return render_template('home.html')

@app.route('/addItem.html')
def add():
    return render_template('addItem.html')

if __name__ == "__main__":
    app.run()
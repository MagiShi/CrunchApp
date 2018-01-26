from flask import Flask, flash, redirect, render_template, request, session, abort


import os
from urllib.parse import urlparse
import psycopg2

app = Flask(__name__)

url = urlparse("postgres://mbgugkwmyyrgpp:08f1f171ba8df81468de5e7d166069757cc545fb163d5cc820407068513b101d@ec2-54-163-237-249.compute-1.amazonaws.com:5432/da0io40vrbg6u0")
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
schema = "schema.sql"
conn = psycopg2.connect(db)
cursor = conn.cursor()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login.html', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    query = "SELECT * FROM registereduser WHERE username = '{0}' AND password = '{1}';".format(username, password)
    print (query)
    cursor.execute(query)
    # print (cursor.fetchone())
    tup = cursor.fetchone()

    if tup is None:
        return render_template('login.html')

    return render_template('home.html')

@app.route('/home.html')
def loggedin():
    return render_template('home.html')
def guest():
    # should look different than a registered user (not able to add, delete, etc)
    return render_template('home.html')

@app.route('/register.html')
def newUser():
    return render_template('register.html')

@app.route('/postregister.html', methods=['POST'])
def register():
    # print ("in here")
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    #Account type not accessed
    accountType = request.form['accountType']
    if accountType == 'studentAccount':
        isAdmin = False
    else:
        isAdmin = True

    query = "INSERT into registereduser values ('{0}', '{1}', '{2}', {3});".format(email, username, password, isAdmin)
    print (query)
    # print (cursor.execute(query))
    # print (cursor.fetchone())
    cursor.execute(query)
    # tup = cursor.fetchone()
    # print (tup)

    return render_template('login.html')

@app.route('/addItem.html')
def add():
    return render_template('addItem.html')

if __name__ == "__main__":
    app.run()
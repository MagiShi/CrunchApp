from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_mail import Mail, Message

import os
from urllib.parse import urlparse
import psycopg2

app = Flask(__name__)

app.config.update(
    # DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'crunch.thracker@gmail.com',
    MAIL_PASSWORD = os.environ['epassword']
    )
mail = Mail(app)

url = urlparse(os.environ['DATABASE_URL'])
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
schema = "schema.sql"
conn = psycopg2.connect(db)
cursor = conn.cursor()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login.html', methods=['POST'])
#method for logging in, on home page.
def login():
    username = request.form['username']
    password = request.form['password']
    error = None

    query = "SELECT * FROM registereduser WHERE username = '{0}' AND password = '{1}';".format(username, password)
    print (query)
    try:
        cursor.execute(query)
        # print (cursor.fetchone())
        tup = cursor.fetchone()

        if tup is None:
            ##Error message for wrong password/username
            error = 'The username or password you have entered is incorrect.'
            return render_template('login.html', error=error)
    except: 
        ##Any errors (there shouldn't be) should be handled here
        query = "rollback;"
        cursor.execute(query)
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

@app.route('/forgotpass.html')
def forgotPass():
    error = 'Please enter email address'
    return render_template('forgotpass.html', error=error)

@app.route('/forgotpass.html', methods=['POST'])
def sendMail():
    email = request.form['email']

    query = "Select password from registereduser Where email = '{0}';".format(email)

    try: 
        cursor.execute(query)
        tup = cursor.fetchone()

        if tup is None:
            ##Error message for wrong password/username

            error = 'The email you have entered is unregistered.'
            return render_template('forgotpass.html', error=error)

        msg = Message("Your password is {0}".format(tup), sender=("crunch.thracker@gmail.com"), recipients=["{0}".format(email)])
        mail.send(msg)
    except Exception as e:
        print (e)
        query = "rollback;"
        cursor.execute(query)
        error = 'Please enter an email'
        return render_template('forgotpass.html', error=error)


    error = 'Email sent'
    return render_template('login.html', error=error)

@app.route('/postregister.html', methods=['POST'])
#def for registering, occurs after clicking registration button
def register():
    # print ("in here")
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    error = None
    
    #Account type not accessed
    accountType = request.form['accountType']
    if accountType == 'studentAccount':
        isAdmin = False
    else:
        isAdmin = True

    if username == '' or email == '' or password == '':
        error = 'Please fill in all fields'
        return render_template('register.html', error=error)

    query = "INSERT into registereduser values ('{0}', '{1}', '{2}', {3});".format(email, username, password, isAdmin)

    try: 
        cursor.execute(query)
        # print ("executed")
    except Exception as e: 
        query = "rollback;"
        cursor.execute(query)

        ##If registration fails
        error = 'Account creation has failed.'
        return render_template('register.html', error=error)

    conn.commit()

    return render_template('home.html')

# renders addItem page
@app.route('/addItem.html')
def add():
    return render_template('addItem.html')


@app.route('/postaddItem.html', methods=['POST'])
def addItem():    
    item_id = request.form['barcode']
    item_name = request.form['itemname']
    description = request.form['description']
    error = None

    if item_id == '' or item_name == '':
        error = 'Item must have a barcode/id and a name'
        return render_template('addItem.html', error=error)
    if description == '':
        description = 'null'

    query = "INSERT into item values ('{0}', '{1}', NULL, false, '{2}');".format(item_id, item_name, description)
    print(query)
    try: 
        cursor.execute(query)
        # print ("executed")
    except Exception as e: 
        query = "rollback;"
        cursor.execute(query)

        ##If item creation fails
        error = 'Item creation has failed.'
        return render_template('addItem.html', error=error)

    conn.commit()
    return render_template('itemDetail.html')


@app.route('/login.html')
def logout():
    return render_template('login.html')

if __name__ == "__main__":
    app.run()
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, json, send_file
from flask_mail import Mail, Message

from werkzeug.utils import secure_filename

import base64
from PIL import Image
from io import BytesIO

import os
from urllib.parse import urlparse
import psycopg2

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = "/tmp/"
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
def welcome():
    # if request.args.get('error') == None:
        # print("here")
        # return render_template('login.html')
    error = request.args.get('error')
    print (repr(error))
    # return render_template('login.html', error=json.loads(error))
    return render_template('login.html', error=error)

@app.route('/postlogin', methods=['POST'])
#method for logging in, on home page.
def login():
    username = request.form['username']
    password = request.form['password']
    error = None

    query = "SELECT * FROM registereduser WHERE username = '{0}' AND password = '{1}';".format(username, password)
    print (query)
    # errors = {"error": "The username or password you have entered is incorrect."}
    try:
        cursor.execute(query)
        # print (cursor.fetchone())
        tup = cursor.fetchone()

        if tup is None:
            ##Error message for wrong password/username
            error = 'The username or password you have entered is incorrect.'
            # errors =  json.dumps(errors)
            # return redirect(url_for('home', error=errors))
            return redirect(url_for('welcome', error=error))
        else:
        	session['user'] = True;
    except: 
        ##Any errors (there shouldn't be) should be handled here
        query = "rollback;"
        cursor.execute(query)
        # errors =  json.dumps(errors)
        # return redirect(url_for('home', error=errors))
        error = 'The username or password you have entered is incorrect.'
        return redirect(url_for('welcome', error=error))
    return redirect(url_for('loggedin'))

@app.route('/home')
def loggedin():
    return render_template('home.html')
def guest():
    # should look different than a registered user (not able to add, delete, etc)
    return render_template('home.html')

@app.route('/register')
def newUser():
    error = request.args.get('error')
    return render_template('register.html', error=error)

@app.route('/forgotpass')
def forgotPass():

    if request.args.get('error') is None:
        error = 'Please enter email address'
    else:
        error = request.args.get('error')
    return render_template('forgotpass.html', error=error)

@app.route('/forgotpass', methods=['POST'])
def sendMail():
    email = request.form['email']

    query = "Select password from registereduser Where email = '{0}';".format(email)

    try: 
        cursor.execute(query)
        tup = cursor.fetchone()

        if tup is None:
            ##Error message for wrong password/username

            error = 'The email you have entered is unregistered.'
            # return render_template('forgotpass.html', error=error)
            return redirect(url_for('forgotPass', error=error))

        msg = Message("Your password is {0}".format(tup), sender=("crunch.thracker@gmail.com"), recipients=["{0}".format(email)])
        mail.send(msg)
    except Exception as e:
        print (e)
        query = "rollback;"
        cursor.execute(query)
        error = 'Please enter an email'
        return redirect(url_for('forgotPass', error=error))


    error = 'Email sent'
    return redirect(url_for('welcome', error=error))

@app.route('/postregister', methods=['POST'])
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
        return redirect(url_for('newUser', error=error))

    query = "INSERT into registereduser values ('{0}', '{1}', '{2}', {3});".format(email, username, password, isAdmin)

    try: 
        cursor.execute(query)
        # print ("executed")
    except Exception as e: 
        query = "rollback;"
        cursor.execute(query)

        ##If registration fails
        error = 'Account creation has failed.'
        return redirect(url_for('newUser', error=error))

    conn.commit()

    return redirect(url_for('loggedin'))

# renders addItem page
@app.route('/addItem')
def add():
    error = request.args.get('error')
    return render_template('addItem.html', error=error)


@app.route('/postaddItem', methods=['POST'])
def addItem():
    if request.form.get("addItemButton"):
        item_id = request.form['barcode']
        # print ("here")
        item_name = request.form['itemname']
        description = request.form['description']
        error = None

        file = None
        try:
            file = request.files['photo1']
        # For only 1 file, if multiple, assume loop through this
        # print ("file")
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except Exception as e:
            print (e)
            filename = None
        # if file == None:
        #     print("NONE")
        # print(type(file))

        if item_id == '' or item_name == '':
            error = 'Item must have a barcode/id and a name'
            return redirect(url_for('add', error=error))
        if description == '':
            description = 'N/A'

        query = "INSERT into item(itemid, itemname, pendingdelete, description) values ('{0}', '{1}',  false, '{2}');".format(item_id, item_name, description)
        print(query)
        # query = None
        try:
            # print (repr(query))
            # print("in try")
            cursor.execute(query)
            # print("exe")
            conn.commit()
            # print("conn")

            
            if filename != None:
                print ("looking for file: " + "tmp/"+filename )
                print ("loading file")
                f = open("/tmp/"+filename,'rb')
                filedata = f.read()
                f.close()
                cursor.execute("UPDATE item SET image[0] = %s WHERE itemid=(%s);", (filedata, item_id))
                conn.commit()

                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            #assuming array for multiple upload
            # imagefiles = request.form['photo']
            # i = 0
            # for image in imagefiles:
            #     f = open(image1file,'rb')
            #     filedata = f.read()
            #     f.close()
            #     cursor.execute("UPDATE item SET image[%d] = %s WHERE itemid=(%s);", (i,filedata, item_id))
            #     conn.commit()
            #     i += 1

            #cursor.execute("INSERT into item values (%s, %s, '{{ \" %s \" }} ', false, %s);", (item_id, item_name, psycopg2.Binary(filedata), description))
            # cursor.execute("INSERT into temptable values (%s, %s, %s, false, %s);", (item_id, item_name, psycopg2.Binary(filedata), description))
            # print ("executed")

        except Exception as e:
            print (e)
            query = "rollback;"
            cursor.execute(query)

            ##If item creation fails
            error = 'Item creation has failed.'
            return redirect(url_for('add', error=error))

        # conn.commit()
        error = 'Item successfully added.'
        return redirect(url_for('getItemInfo', item_id=item_id, error=error))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/deleteItem/<item_id>', methods=['POST'])
def deleteItemFlag(item_id):
    item_id = item_id
    query = "UPDATE item set pendingdelete=true where itemid='{0}';".format(item_id)
    try: 
        cursor.execute(query)
        # print ("executed")
    except Exception as e: 
        query = "rollback;"
        cursor.execute(query)

        ##If item creation fails
        error = 'Item deletion has failed.'
        return redirect(url_for('getItemInfo', item_id=item_id, error=error))

    conn.commit()
    error = 'Item marked for deletion! Waiting for action by Admin'
    return redirect(url_for('getItemInfo', item_id=item_id, error=error))

@app.route('/item/<item_id>', methods=['POST', 'GET'])
def getItemInfo(item_id):

    error = request.args.get('error')
    item_id = item_id
    itemname = None
    image = None
    description = None
    delete = None
    
    #query = "SELECT * FROM item WHERE itemid='{0}';".format(item_id)
    try: 
        cursor.execute("SELECT itemname FROM item WHERE itemid='{0}';".format(item_id))
        itemname = cursor.fetchone()
        cursor.execute("SELECT image FROM item WHERE itemid='{0}';".format(item_id))
        image = cursor.fetchone()
        # image = list(cursor)
        cursor.execute("SELECT description FROM item WHERE itemid='{0}';".format(item_id))
        description = cursor.fetchone()
        cursor.execute("SELECT pendingdelete FROM item WHERE itemid='{0}';".format(item_id))
        delete = cursor.fetchone()
        # print (image)
        imagedata = []
        if image[0] != None:
            for i in image[0]:
                # print (bytes(i))
                # imgstr = bytes(i)
                # print(binascii.hexlify(bytes(i)))
                # # imgstr = 'data:image/jpeg;base64' + base64.b64encode(bytes(i))
                # imagedata.append(imgstr)
                image_data = bytes(i)
                encoded = base64.b64encode(image_data)
                stren = encoded.decode("utf-8")
                imagedata.append(stren)

                # to show image as a seperate pop-up (?) --local only
                # data = base64.b64decode(encoded)
                # image1 = Image.open(BytesIO(image_data))
                # image1.show()
                print (i)
        
    except Exception as e: 
        print (e)
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))

    #NOTE:  image should be a list/array
    return render_template('item.html', itemid=item_id, itemname=itemname, image=imagedata, description=description, delete=delete, error=error)
    # print("here")
    # return render_template('item.html', error=error)

# renders editItem page
@app.route('/editItem/<item_id>', methods=["POST", "GET"])
def edit(item_id):

    error = request.args.get('error')
    item_id = item_id
    #itemname = request.form['itemname']
    #description = request.form['description']
    itemname = None
    image = None
    description = None
    delete = None
    
    #query = "SELECT * FROM item WHERE itemid='{0}';".format(item_id)
    try: 
        #query = ("UPDATE item SET itemname ='{2}', description ='{1}' WHERE itemid='{0}';".format(item_id, itemname, description))
        #cursor.execute(query)
        cursor.execute("SELECT itemname FROM item WHERE itemid='{0}';".format(item_id))
        itemname = cursor.fetchone()
        cursor.execute("SELECT image FROM item WHERE itemid='{0}';".format(item_id))
        image = cursor.fetchall()
        cursor.execute("SELECT description FROM item WHERE itemid='{0}';".format(item_id))
        description = cursor.fetchone()
        cursor.execute("SELECT pendingdelete FROM item WHERE itemid='{0}';".format(item_id))
        delete = cursor.fetchone()
        #print ("executed")
    except Exception as e: 
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))

    return render_template('editItem.html', itemid=item_id, itemname=itemname, image=image, description=description, delete=delete, error=error)
    #return redirect(url_for('getItemInfo', item_id=item_id))
@app.route('/posteditItem/<item_id>', methods=["POST"])
def editItem(item_id):
    item_id = item_id
    itemname = request.form['itemname']
    description = request.form['description']
    try: 
        query = ("UPDATE item SET itemname ='{1}', description ='{2}' WHERE itemid='{0}';".format(item_id, itemname, description))
        #query = ("UPDATE item SET itemname = '{1}' WHERE itemid= '{0}';".format(item_id, itemname, description))
        cursor.execute(query)
        conn.commit()
        error = 'Item successfully edited.'
    except Exception as e: 
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))
    return redirect(url_for('getItemInfo', item_id=item_id, error=error))
if __name__ == "__main__":
    app.run()


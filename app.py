from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, json, send_file
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse
import psycopg2

## only for local image rendering
# from PIL import Image

import base64
from io import BytesIO

import functions

app = Flask(__name__)
app.secret_key = os.urandom(24)

#configuring upload_folder variable
app.config['UPLOAD_FOLDER'] = "/tmp/"

app.config.update(
    # DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'crunch.thracker@gmail.com',
    # MAIL_PASSWORD = os.environ['epassword']
    )
mail = Mail(app)

#configuring database url and path
url = urlparse(os.environ['DATABASE_URL'])
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
schema = "schema.sql"
#connecting a cursor for the database
conn = psycopg2.connect(db)
cursor = conn.cursor()

#welcome page rendering
@app.route('/')
def welcome():
    error = request.args.get('error')
    print (repr(error))
    return render_template('login.html', error=error)

#method after clicking on login button
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
        tup = cursor.fetchone()

        if tup is None:
            ##Error message for wrong password/username
            error = 'The username or password you have entered is incorrect.'
            return redirect(url_for('welcome', error=error))
        else:
        	session['user'] = True;
    except: 
        ##Any errors should be handled here
        query = "rollback;"
        cursor.execute(query)
        error = 'The username or password you have entered is incorrect.'
        return redirect(url_for('welcome', error=error))
    return redirect(url_for('loggedin'))

#rendering home page after logging in
@app.route('/home')
def loggedin():
    itemname = None
    image = None
    itemid = None
    itemidQuery = "SELECT itemid FROM item;"
    itemNameQuery = "SELECT itemname FROM item;"
    imageQuery = "SELECT image1 FROM item;"
    cursor.execute(itemidQuery)
    itemid = cursor.fetchall()
    cursor.execute(itemNameQuery)
    itemname = cursor.fetchall()
    cursor.execute(imageQuery)
    image = cursor.fetchall()

    return render_template('home.html', itemid=itemid, itemname=itemname, image=image)
def guest():
    # should look different than a registered user (not able to add, delete, etc)
    return render_template('home.html')

#rendering registration page
@app.route('/register')
def newUser():
    error = request.args.get('error')
    return render_template('register.html', error=error)

#rendering forgot password page
@app.route('/forgotpass')
def forgotPass():
    if request.args.get('error') is None:
        error = 'Please enter email address'
    else:
        error = request.args.get('error')
    return render_template('forgotpass.html', error=error)

#For after clicking on forgot password button 
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

#def for registering, occurs after clicking registration button
@app.route('/postregister', methods=['POST'])
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

# Add item to the database, after button is clicked on add item page.
@app.route('/postaddItem', methods=['POST'])
def addItem():
    if request.form.get("add-item-button"):

        #initialize all values from the html form here
        item_id = request.form['barcode']
        item_name = request.form['itemname']
        description = request.form['description']
        try: 
            sex = request.form['genderSelect']
        except: 
            sex = None
        
        # try: 
        #     condition = request.form['condition']
        # except: 
        #     condition = None

        # try:
        #     timeperiodL = request.form.getlist('colorSelect')
        #     # print (colorL)
        #     timeperiod = '{'
        #     for c in range(len(timeperiodL)):
        #         if c >= len(timeperiodL) -1:
        #             timeperiod += '{0}'.format(timeperiodL[c])
        #         else: 
        #             timeperiod += '{0}, '.format(timeperiodL[c])
        #     timeperiod += '}'
        # except:
        #     timeperiod = None

        # try:
        #     cultureL = request.form.getlist('colorSelect')
        #     # print (colorL)
        #     culture = '{'
        #     for c in range(len(cultureL)):
        #         if c >= len(cultureL) -1:
        #             culture += '{0}'.format(cultureL[c])
        #         else: 
        #             culture += '{0}, '.format(cultureL[c])
        #     culture += '}'
        # except:
        #     culture = None

        try:
            colorL = request.form.getlist('colorSelect')
            # print (colorL)
            color = '{'
            for c in range(len(colorL)):
                if c >= len(colorL) -1:
                    color += '{0}'.format(colorL[c])
                else: 
                    color += '{0}, '.format(colorL[c])
            color += '}'
            # print (color)
        except:
            color = None

        try:
            size = request.form['sizeSelect']
        except:
            size = None
        try:        
            itemtype = request.form['typeSelect']
        except:
            itemtype = None
        # try:
        #     itype = request.form['itypeSelect']
        # except:
        #     itype = None
        error = None
        file1 = None
        file2 = None
        file3 = None

        #for image1, temp image upload
        try:
            file1 = request.files['photo1']
            if file1 != None and file1.filename != '':
                filename1 = secure_filename(file1.filename)
                file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            else:
                filename1 = None
        except Exception as e:
            print ("file1", e)
            filename1 = None
        
        #for image2, temp image upload
        try:
            file2 = request.files['photo2']
            if file2 != None and file2.filename != '':
                filename2 = secure_filename(file2.filename)
                file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            else:
                filename2 = None
        except Exception as e:
            print ("file2", e)
            filename2 = None
        
        #for image3, temp image upload
        try:
            file3 = request.files['photo3']
            if file3 != None and file3.filename != '':
                print (file3)
                filename3 = secure_filename(file3.filename)
                file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
            else:
                filename3 = None

        except Exception as e:
            print ("file3", e)
            filename3 = None

        if item_id == '' or item_name == '':
            error = 'Item must have a barcode/id and a name'
            return redirect(url_for('add', error=error))
        if description == '':
            description = 'N/A'

        # query = "INSERT into item(itemid, itemname, pendingdelete, description, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable) values ('{0}', '{1}',  false, '{2}');".format(item_id, item_name, description)

        # charlist = [item_id, item_name, description, sex, condition, timeperiod, culture, color, size, itemtype, itype]
        # query = "INSERT into item(itemid, itemname, description, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable, pendingdelete) values ("

        #for mult
        charlist = [item_id, item_name, description, sex, color, size, itemtype]
        query = "INSERT into item(itemid, itemname, description, sex, color, size, itemtype, isavailable, pendingdelete) values ("


        for char in charlist:
            if char != None:
                query += "'{0}', ".format(char)
            else:
                query += " NULL, "

        query += " true, false);"

        print(query)
        try:
            cursor.execute(query)
            conn.commit()

            if filename1 != None:
                print ("looking for file: " + "tmp/"+ filename1 )
                print ("loading file")
                f = open("/tmp/"+filename1,'rb')
                filedata = f.read()
                f.close()
                cursor.execute("UPDATE item SET image1 = %s WHERE itemid=(%s);", (filedata, item_id))
                conn.commit()
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

            if filename2 != None:
                print ("looking for file: " + "tmp/"+ filename2 )
                print ("loading file")
                f = open("/tmp/"+filename2,'rb')
                filedata = f.read()
                f.close()
                cursor.execute("UPDATE item SET image2 = %s WHERE itemid=(%s);", (filedata, item_id))
                conn.commit()
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

            if filename3 != None:
                print ("looking for file: " + "tmp/"+ filename3 )
                print ("loading file")
                f = open("/tmp/"+filename3,'rb')
                filedata = f.read()
                f.close()
                cursor.execute("UPDATE item SET image3 = %s WHERE itemid=(%s);", (filedata, item_id))
                conn.commit()
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename3))

        except Exception as e:
            print (e)
            query = "rollback;"
            cursor.execute(query)

            ##If item creation fails
            error = 'Item creation has failed.'
            return redirect(url_for('add', error=error))

        error = 'Item successfully added.'
        return redirect(url_for('getItemInfo', item_id=item_id, error=error))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/editFolders/<item_id>', methods=["POST", "GET"])
def toEditProdFolders(item_id):
    item_id = item_id
    error = None
    itemname = None
    
    #query = "SELECT * FROM item WHERE itemid='{0}';".format(item_id)
    try: 
        cursor.execute("SELECT itemname FROM item WHERE itemid='{0}';".format(item_id))
        itemname = cursor.fetchone()

    except Exception as e: 
        print (e)
        # cursor.execute("rollback;")

        # ##If item does not exist etc
        # error = 'Item information cannot be retrieved'
        # return redirect(url_for('loggedin', error=error))

    return render_template('editProdFolders.html', itemid=item_id, itemname=itemname, error=error)

@app.route('/posteditFolders/<item_id>', methods=['POST'])
def editProdFolders(item_id):
    item_id = item_id
    error = None
    return redirect(url_for('getItemInfo', item_id=item_id, error=error))

# render Production Folders page with all folders in the database
@app.route('/folders', methods=['POST', 'GET'])
def prodFolders():
    foldername = None
    folderid = None
    folderidQuery = "SELECT folderid FROM folder;"
    folderNameQuery = "SELECT foldername FROM folder;"
    cursor.execute(folderidQuery)
    folderid = cursor.fetchall()
    cursor.execute(folderNameQuery)
    foldername = cursor.fetchall()
    error = request.args.get('error')

    return render_template('prodFolders.html', folderid=folderid, foldername=foldername, error=error)

# Update the name of production folder
@app.route('/postrenameFolders', methods=['POST'])
def renameFolders():
    # get the folder new name from the user's input
    foldername = request.form['foldername']
    # get the folder id from the value of 'Save' button
    folderid = request.form['saveNameButton']
    try:
        query = "UPDATE folder SET foldername ='{1}' WHERE folderid='{0}';".format(folderid, foldername)
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        cursor.execute("rollback;")

        ##If folder does not exist etc
        error = 'Folder information cannot be retrieved'
        return redirect(url_for('prodFolders', error=error))
    # Refresh the Production Folders page with the updated name of the folder
    return redirect(url_for('prodFolders'))


@app.route('/deleteItem/<item_id>', methods=['POST'])
def deleteItemFlag(item_id):
    item_id = item_id
    query = "UPDATE item set pendingdelete=true where itemid='{0}';".format(item_id)
    try: 
        cursor.execute(query)
    except Exception as e: 
        query = "rollback;"
        cursor.execute(query)

        ##If item creation fails
        error = 'Item deletion has failed.'
        return redirect(url_for('getItemInfo', item_id=item_id, error=error))

    conn.commit()
    error = 'Item marked for deletion! Waiting for action by Admin'
    return redirect(url_for('getItemInfo', item_id=item_id, error=error))

#pre-loading information for a specific item
@app.route('/item/<item_id>', methods=['POST', 'GET'])
def getItemInfo(item_id):
    # declare all variables
    error = request.args.get('error')
    item_id = item_id
    itemname = None
    image1 = None
    image2 = None
    image3 = None
    description = None
    pendingdelete = None
    sex = None
    # condition = None
    # timeperiod = None
    # culture = None
    color = None
    size = None
    itemtype = None
    # itype = None
    isavailable = None
    
    try: 
        # calls functions.py method
        itemname, image1, image2, image3, description, pendingdelete, sex, color, size, itemtype, isavailable = functions.getInfo(item_id, cursor)
        # itemname, image1, image2, image3, description, pendingdelete, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable = getInfo(item_id)

        imagedata1 = []
        if image1[0] != None:
            imagedata1 = functions.getImagedata(image1)

        imagedata2 = []
        if image2[0] != None:
            imagedata2 = functions.getImagedata(image2)

        imagedata3 = []
        if image3[0] != None:
            imagedata3 = functions.getImagedata(image3)
        
    except Exception as e: 
        print (e)
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))

    ##culture, color, timeperiod are all arrays
    return render_template('item.html', itemid=item_id, itemname=itemname, image=imagedata1, image2=imagedata2, image3=imagedata3, description=description, delete=pendingdelete, sex=sex, color=color, size=size, itemtype=itemtype, isavailable=isavailable, error=error)
    # return render_template('item.html', itemid=item_id, itemname=itemname, image=imagedata1, image2=imagedata2, image3=imagedata3, description=description, delete=pendingdelete, sex=sex, condition=condition, timeperiod=timeperiod, culture=culture color=color, size=size, itemtype=itemtype, itype=itype, isavailable=isavailable, error=error)

# renders editItem page
@app.route('/editItem/<item_id>', methods=["POST", "GET"])
def edit(item_id):
    # declare all variables
    error = request.args.get('error')
    item_id = item_id
    itemname = None
    image1 = None
    image2 = None
    image3 = None
    description = None
    pendingdelete = None
    sex = None
    # condition = None
    # timeperiod = None
    # culture = None
    color = None
    size = None
    itemtype = None
    # itype = None
    isavailable = None
    
    try: 
        # calls functions.py method
        itemname, _, _, _, description, pendingdelete, sex, color, size, itemtype, isavailable = functions.getInfo(item_id, cursor)
        # itemname, image1, image2, image3, description, pendingdelete, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable = getInfo(item_id)

        #print ("executed")
    except Exception as e: 
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))

    ##culture, color, timeperiod are all arrays
    return render_template('editItem.html', itemid=item_id, itemname=itemname, description=description, delete=pendingdelete, sex=sex, color=color, size=size, itemtype=itemtype, isavailable=isavailable, error=error)
    # return render_template('editItem.html', itemid=item_id, itemname=itemname, description=description, delete=pendingdelete, sex=sex, condition=condition, timeperiod=timeperiod, culture=culture color=color, size=size, itemtype=itemtype, itype=itype, isavailable=isavailable, error=error)
    # return render_template('editItem.html', itemid=item_id, itemname=itemname, image=imagedata1, image2=imagedata2, image3=imagedata3, description=description, delete=pendingdelete, sex=sex, condition=condition, timeperiod=timeperiod, culture=culture color=color, size=size, itemtype=itemtype, itype=itype, isavailable=isavailable, error=error)

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




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

#file with helper functions
import functions

import json

#for current date
import datetime

import ast

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
    MAIL_PASSWORD = os.environ['epassword']
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

    query = "SELECT email FROM registereduser WHERE username = '{0}' AND password = '{1}';".format(username, password)
    print (query)
    # errors = {"error": "The username or password you have entered is incorrect."}
    try:
        cursor.execute(query)
        email_list = cursor.fetchone()

        # print (email_list)

        if email_list is None:
            ##Error message for wrong password/username
            error = 'The username or password you have entered is incorrect.'
            return redirect(url_for('welcome', error=error))
        else:
            ## Else set session value as the user email
            session['user'] = email_list[0]
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
    for x in image:
        imagedata = []
        if x[0] != None:
            imagedata = functions.getImagedata(x)
            x = imagedata

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
        
        try: 
            condition = request.form['condition']
        except: 
            condition = None

        try:
            timeperiodL = request.form.getlist('timeSelect')
            # print (colorL)
            timeperiod = '{'
            for c in range(len(timeperiodL)):
                if c >= len(timeperiodL) -1:
                    timeperiod += '{0}'.format(timeperiodL[c])
                else: 
                    timeperiod += '{0}, '.format(timeperiodL[c])
            timeperiod += '}'
        except:
            timeperiod = None

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
        charlist = [item_id, item_name, description, sex, condition, timeperiod, color, size, itemtype]
        query = "INSERT into item(itemid, itemname, description, sex, condition, timeperiod, color, size, itemtype, isavailable, pendingdelete) values ("


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
                functions.setImageInDatabase(filename1, item_id, cursor, conn, app.config['UPLOAD_FOLDER'])

            if filename2 != None:
                functions.setImageInDatabase(filename2, item_id, cursor, conn, app.config['UPLOAD_FOLDER'])

            if filename3 != None:
                functions.setImageInDatabase(filename3, item_id, cursor, conn, app.config['UPLOAD_FOLDER'])

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

@app.route('/setReservation/<item_id>', methods=["POST", "GET"])
def reserveItem(item_id):
    # print ("pe", passed_error)
    error = None
    # passed_error = None
    # if type(item_id) == list:
    #     itemid = item_id[0]
    #     passed_error = item_id[1]
    # else: 
    #     itemid = item_id

    # print(error)
    try:
        #returns all reservations with that item id
        cursor.execute("SELECT * from reservation where itemid='{0}' and (status='current' or status='future');".format(item_id))

        all_reservations_this_item = cursor.fetchall()
        index = 0
        for c in all_reservations_this_item:
            all_reservations_this_item[index] = c[:2] + (c[2].strftime('%Y-%m-%d'), c[3].strftime('%Y-%m-%d')) + c[4:]
            index += 1
        ## Convert the list of tuples to JSON so it can be readable in JavaScript.
        ## [('a','b'),('d','c')] -> [['a','b],['c','d']]
        ## default=str turns datetime.date into str, because it is not JSON serializable
        all_reservations_this_item = json.dumps(all_reservations_this_item, default=str)
    except Exception as e:
        cursor.execute("rollback;")
        print(e)
        # if passed_error:
            # error = passed_error
        # else: 
        error = "Cannot retrieve reservation information for item {0}.".format(itemid)
        return render_template('setReservation.html', itemid=item_id, error=error)
    return render_template('setReservation.html', itemid=item_id, all_reservations=all_reservations_this_item, error=error)


@app.route('/postSetReservation/<item_id>', methods=["POST", "GET"])
def postReserveItem(item_id):
    #retreive information for reservation creation
    itemid = item_id
    email = session.get('user')
    unformatted_date = (request.form.get('daterange').split())
    start_date = unformatted_date[0]
    end_date = unformatted_date[2]

    start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
    end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()

    # This does not check for past, because users should not be able to make reservations that start in the past
    # This would also mess with the scheduler if "past" status tuple are reserved.
    status = None
    if start_date <= datetime.datetime.now():
        status="current"
    else: 
        status="future"
    error = None

    try:
        #returns all reservations with that item id
        query = "INSERT into reservation VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(email, item_id, start_date, end_date, status)
        print (query)
        cursor.execute(query)
        conn.commit()
        error = "Your reservation for item with barcode {0} has been reserved from {1} to {2}".format(itemid, start_date, end_date)

    except Exception as e:
        cursor.execute("rollback;")
        # print("Error on item reservation page:", e)
        passed_error = "Your reservation for item with barcode {0} cannot be created for dates {1} to {2}".format(itemid, start_date, end_date)
        try:
            #returns all reservations with that item id
            cursor.execute("SELECT * from reservation where itemid='{0}';".format(item_id))

            all_reservations_this_item = cursor.fetchall()
            index = 0
            for c in all_reservations_this_item:
                all_reservations_this_item[index] = c[:2] + (c[2].strftime('%Y-%m-%d'), c[3].strftime('%Y-%m-%d')) + c[4:]
                index += 1
            ## Convert the list of tuples to JSON so it can be readable in JavaScript.
            ## [('a','b'),('d','c')] -> [['a','b],['c','d']]
            ## default=str turns datetime.date into str, because it is not JSON serializable
            all_reservations_this_item = json.dumps(all_reservations_this_item, default=str)

            ## The datepicker bootstrap automatically chooses today as start and end date in setReservation page.
            ## Ensure the default start and end dates are valid. They are should be the closest available date to today.
            cursor.execute("SELECT * from reservation where itemid='{0}' and status='current';".format(item_id))
            # only get the start, and end. This list of tuples should have length of 1.
            current_item_reservation = [ (x[2],x[3]) for x in cursor.fetchall()]

            cursor.execute("SELECT * from reservation where itemid='{0}' and status='future';".format(item_id))
            # only get the start, and end.
            future_item_reservations = [ (x[2],x[3]) for x in cursor.fetchall()]
            # sort the list by the ascending start date.
            future_item_reservations = sorted(future_item_reservations)

            # today's date. Type: datetime.date ; Format: '%Y-%m-%d'
            today = datetime.datetime.now()
            today = today.date()

            default_start = today
            if len(current_item_reservation) > 0:
                default_start = current_item_reservation[0][1] + datetime.timedelta(days=1)

            if len(future_item_reservations) > 0:
                index = 0
                for c in future_item_reservations:
                    if c[0] == default_start:
                        default_start = c[1] + datetime.timedelta(days=1)
                    else:
                        break

            default_start = default_start.strftime('%m/%d/%Y')

        except Exception as e:
            cursor.execute("rollback;")
            print(e)

            error = "Cannot retrieve reservation information for item {0}.".format(item_id)
            return render_template('setReservation.html', itemid=item_id, error=error)

        return render_template('setReservation.html', itemid=item_id, all_reservations=all_reservations_this_item, default_start=default_start, error=passed_error)

    return redirect(url_for('getItemInfo', item_id=itemid, error=error))

@app.route('/editReservation/<path:data>', methods=["POST", "GET"])
def editReservation(data): 

    import ast
    d = ast.literal_eval(data)

    error = None
    email = session.get('user')
    item_id = d.get('itemId').split()[1]

    calendar = d.get('calendarResult')
    split_cal = calendar.split()
    start_date = split_cal[0]
    end_date = split_cal[2]
    old_start_date = d.get('prev_start').split()[0]

    # print(item_id)
    # print(start_date)
    # print(end_date)
    # print(old_start_date)
    
    try:
        query = "UPDATE reservation SET startdate='{0}' , enddate='{1}' WHERE email='{2}' and itemid='{3}' and startdate='{4}';".format(start_date, end_date, email, item_id, old_start_date)
        print(query)
        cursor.execute(query)
        conn.commit()
        error = "Update successful!"
    except Exception as e:
        cursor.execute("rollback;")
        print(e)
        error = "Cannot update date"
        return redirect(url_for('reservations', error=error))
    return redirect(url_for('reservations', error=error))
 


@app.route('/editFolders/<item_id>', methods=["POST", "GET"])
def toEditProdFolders(item_id):
    item_id = item_id
    error = None
    itemname = None
    foldername = None

    folderNameQuery = "SELECT foldername FROM folder where pendingdelete=false;"
    cursor.execute(folderNameQuery)
    foldername = cursor.fetchall()
    query = "SELECT foldername FROM folder where pendingdelete=true;"
    cursor.execute(query)
    # code bellow converts the tuple into a simple arraylist in order to pass the data directly into JS.
    # ex: [('Folder 1',),('Folder 2',)] -> ['Folder 1', 'Folder 2']
    deletedfolders = [ x[0] for x in cursor.fetchall()]
    error = request.args.get('error')

    
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

    return render_template('editProdFolders.html', itemid=item_id, itemname=itemname, foldername=foldername, deletedfolders=deletedfolders, error=error)

@app.route('/posteditFolders/<item_id>', methods=['POST'])
def editProdFolders(item_id):
    item_id = item_id
    error = None
    return redirect(url_for('getItemInfo', item_id=item_id, error=error))

# render Production Folders page with all folders in the database
@app.route('/folders', methods=['POST', 'GET'])
def prodFolders():
    foldernames = None
    folderNameQuery = "SELECT foldername FROM folder where pendingdelete=false;"
    cursor.execute(folderNameQuery)
    foldernames = cursor.fetchall()

    query = "SELECT foldername FROM folder where pendingdelete=true;"
    cursor.execute(query)
    # code bellow converts the tuple into a simple arraylist in order to pass the data directly into JS.
    # ex: [('Folder 1',),('Folder 2',)] -> ['Folder 1', 'Folder 2']
    deletedfolders = [ x[0] for x in cursor.fetchall()]

    error = request.args.get('error')
    # print (foldernames)

    return render_template('prodFolders.html', foldernames=foldernames, deletedfolders=deletedfolders, error=error)

# Update the name of production folder
@app.route('/postrenameFolder', methods=['POST'])
def renameFolder():
    # get the folder new name from the user's input
    folderNewName = request.form['foldername']
    # get the folder id from the value of 'Save' button
    folderCurrentname = request.form['saveNameButton']
    try:
        query = "UPDATE folder SET foldername ='{1}' WHERE foldername='{0}';".format(folderCurrentname, folderNewName)
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        cursor.execute("rollback;")

        ##If folder does not exist etc
        error = 'Folder information cannot be retrieved'
        return redirect(url_for('prodFolders', error=error))
    # Refresh the Production Folders page with the updated name of the folder
    return redirect(url_for('prodFolders'))

@app.route('/folders/<foldername>', methods=['POST', 'GET'])
def folderContents(foldername):
    error = request.args.get('error')
    foldername = foldername
    # try:
    # except Exception as e:
    #     cursor.execute("rollback;")

    #     ##If folder does not exist etc
    #     error = 'Folder information cannot be retrieved'
    #     return redirect(url_for('prodFolders', error=error))
    # # Refresh the Production Folders page with the updated name of the folder
    return render_template('prodFolderContents.html', error=error, foldername = foldername)

# render My Reservations page with all reservations in the database for that user
@app.route('/reservations', methods=['POST', 'GET'])
def reservations():
    try:

        # checks to see if the reservation statuses need to be updated.
        changedday, day = functions.updateLastAccess(cursor, conn)

        # changedpast: a bool value to see if the number of past reservations 
        # per user needs to be checked because a status has been changed to past
        changedpast = False

        # if the date is different, we need to update the statuses, 
        if changedday:
            changedpast = functions.updateReservationStatus(cursor, conn, day)
        # print (changedpast)

        # if changedpast return true, this means that we need to check to see that there are only 3 past reservations per user.
        if changedpast:
            functions.checkNumOfPastReservations(cursor, conn)

        #At this point, all updates have been done for the database.

        #get the email of the user
        email = session.get('user')

        # query for all past reservations for a user
        # query = "SELECT * from reservation where email='{0}' and status='past';".format(email)
        query = "SELECT email, reservation.itemid, startdate, enddate, status, itemname FROM reservation, item WHERE email='{0}' and item.itemid=reservation.itemid and status='past';".format(email)
        cursor.execute(query)
        past_user_reservations = cursor.fetchall()
        index = 0
        for c in past_user_reservations:
            past_user_reservations[index] = c[:2] + (c[2].strftime('%m/%d/%Y'), c[3].strftime('%m/%d/%Y')) + c[4:]
            index += 1

            # print c

        # query for all current reservations for a user
        query = "SELECT email, reservation.itemid, startdate, enddate, status, itemname FROM reservation, item WHERE email='{0}' and item.itemid=reservation.itemid and status='current';".format(email)
        cursor.execute(query)
        current_user_reservations = cursor.fetchall()
        index = 0
        for c in current_user_reservations:
            current_user_reservations[index] = c[:2] + (c[2].strftime('%m/%d/%Y'), c[3].strftime('%m/%d/%Y')) + c[4:]
            index += 1

        # query for all future reservations for a user
        query = "SELECT email, reservation.itemid, startdate, enddate, status, itemname FROM reservation, item WHERE email='{0}' and item.itemid=reservation.itemid and status='future';".format(email)
        cursor.execute(query)
        future_user_reservations = cursor.fetchall()
        index = 0
        editable_reservations = []
        for c in future_user_reservations:
            future_user_reservations[index] = c[:2] + (c[2].strftime('%m/%d/%Y'), c[3].strftime('%m/%d/%Y')) + c[4:]
            index += 1
            if c[1] not in editable_reservations:
                editable_reservations.append(c[1])

        #returns all reservations as a whole (needed to know item availability)
        #but only contains items in user has reserved, excluding the past reservations
        query = "SELECT email, reservation.itemid, startdate, enddate, status, itemname FROM reservation, item WHERE  item.itemid=reservation.itemid and (status='current' or status='future');".format(email)
        cursor.execute(query)
        all_reservations = cursor.fetchall()
        index = 0
        for c in all_reservations:
            if c[1] in editable_reservations:
                all_reservations[index] = c[:2] + (c[2].strftime('%Y-%m-%d'), c[3].strftime('%Y-%m-%d')) + c[4:]
                index += 1
            else:
                all_reservations.pop(index)

        ## Convert the list of tuples to JSON so it can be readable in JavaScript.
        ## [('a','b'),('d','c')] -> [['a','b],['c','d']]
        ## default=str turns datetime.date into str, because it is not JSON serializable
        all_reservations = json.dumps(all_reservations, default=str)

    except Exception as e:
        cursor.execute("rollback;")
        print("Error: ", e)
        error = "Cannot find your reservations"
        return render_template('reservations.html', error=error)

    # allreservations gives all reservations in the system
    # past_user_reservations gives the specific user's past reservations (should only have last 3)
    # current gives the specific user's current reservations 
    # future gives the specific user's future reservations  
    return render_template('reservations.html', past_user_reservations=past_user_reservations,  current_user_reservations=current_user_reservations,  future_user_reservations=future_user_reservations, all_reservations=all_reservations)


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

    start_date = None
    end_date = None
    is_reserved=False

    
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

        query = "SELECT startdate, enddate FROM reservation WHERE itemid='{0}' and status='current';".format(item_id)
        cursor.execute(query)
        # print (query)
        current_reservation = cursor.fetchone()
        print(current_reservation)
        if current_reservation != None:

            start_date = str(current_reservation[0])
            end_date = str(current_reservation[1])
            is_reserved = True

    except Exception as e: 
        print (e)
        cursor.execute("rollback;")

        ##If item does not exist etc
        error = 'Item information cannot be retrieved'
        return redirect(url_for('loggedin', error=error))

    ##culture, color, timeperiod are all arrays

    return render_template('item.html', itemid=item_id, itemname=itemname, image=imagedata1, image2=imagedata2, image3=imagedata3, description=description, delete=pendingdelete, sex=sex, color=color, size=size, itemtype=itemtype, isavailable=isavailable, error=error, r_start=start_date, r_end=end_date, iscurrentlyreserved=is_reserved)
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

@app.route('/filtered', methods=["POST"])
def filterItems():
    # proptype = request.form.getlist('prop-type')
    # clothingtype = request.form.getlist('clothing-type')
    timeperiod = request.form.getlist('time-period')
    # culture = request.form.getlist('region')
    sex = request.form.getlist('sex')
    color = request.form.getlist('color')
    size = request.form.getlist('size')
    condition = request.form.getlist('condition')
    availability = request.form.getlist('availability')
    isavailable = []
    for a in availability:
        if a == 'available':
            isavailable.append(True)
        elif a == 'unavailable':
            isavailable.append(False)


    char2val = {}
    char2val['timeperiod'] = timeperiod
    char2val['sex'] = sex
    char2val['color'] = color
    char2val['size'] = size
    char2val['condition'] = condition
    char2val['isavailable'] = isavailable

    # charlist = [proptype, clothingtype, timeperiod, culture, sex, color, size, condition, availability]
    char_array_enum_list = ['timeperiod', 'color']
    char_enum_list = ['sex', 'size', 'condition', 'isavailable']
    charArrayBool = False
    charBool = False

    for c in char_array_enum_list:
        if char2val.get(c):
            charArrayBool = True
    for c in char_enum_list:
        if char2val.get(c):
            charBool = True
    # print (charArrayBool)
    # print (charBool)

    query = "SELECT itemid FROM item" 

    if charBool or charArrayBool:
        query += " WHERE "

    newQ = True #flag for new query

    ##Deal with those stored as arrays ['timeperiod', 'color']
    if charArrayBool:
        for c in char_array_enum_list:
            filterCharList = char2val.get(c)
            # print (c, "   ", filterCharList)

            newChar = True #flag for filterCharList, new char
            for char in filterCharList:

                #if first query part
                if newQ:
                    query += "('{0}' = ANY({1})".format(char, c)
                    newQ = False
                    newChar = False
                #if first for the particular characteristic
                elif newChar:
                    query += " AND ('{0}' = ANY({1})".format(char, c)
                    newChar = False
                else:
                    query += " OR '{0}' = ANY({1})".format(char, c)
            if filterCharList:
                query += ")"

    #Filtering based on other attributes ['sex', 'size', 'condition', 'isavailable']
    if charBool:
        for c in char_enum_list:
            filterCharList = char2val.get(c)
            # print (filterCharList)
            newChar = True #counter for filterCharList
            for char in filterCharList:

                #if first query part
                if newQ:
                    query += "({0} = '{1}'".format(c, char)
                    newQ = False
                    newChar = False
                #if first for the particular characteristic
                elif newChar:
                    query += " AND ({0} = '{1}'".format(c, char)
                    newChar = False
                else:
                    query += " OR {0} = '{1}'".format(c, char)
            if filterCharList:
                query += ")"

    query += ";"

    try: 
        cursor.execute(query)
        #conn.commit()
        itemid = cursor.fetchall()
        error = 'Items filtered (temp message)'
    except Exception as e: 
        cursor.execute("rollback;")

        ##Error
        error = 'Cannot filter'
        return redirect(url_for('loggedin', error=error))
    return render_template('homefiltered.html', itemid=itemid, error=error)

#Adding a new folder 
@app.route('/addFolder', methods=["POST"])
def addFolder():
    foldername = request.form['foldername']
    try: 
        query = "INSERT into folder VALUES ('{0}', false);".format(foldername)
        cursor.execute(query)
        conn.commit()

        # functions.createNewFolder(foldername, cursor, conn)
        error = "Folder '{0}' added".format(foldername) #Temp message?
    except Exception as e: 
        cursor.execute("rollback;")

        ##If folder should not have passed checks (should not happen)
        error = 'Folder cannot be created'
        return redirect(url_for('addFolderButton', error=error))

    item_id = request.form.get('addFolderButton')

    # checking to see where redirect, depending on if there is an item_id
    if item_id:
        return redirect(url_for('toEditProdFolders', item_id=item_id, error=error))
    else:
        return redirect(url_for('prodFolders', error=error))

#Deleting a new folder 
@app.route('/deleteFolder/', methods=["POST"])
def deleteFolder():
    foldername = request.form['foldername']
    # print (request.form)
    try: 
        query = "UPDATE folder set pendingdelete=true where foldername='{0}';".format(foldername)
        cursor.execute(query)
        conn.commit()

        # functions.createNewFolder(foldername, cursor, conn)
        error = "Folder '{0}' pending deletion".format(foldername) #Temp message
    except Exception as e: 
        cursor.execute("rollback;")

        ##If folder should not have passed checks (should not happen)
        error = 'Cannot delete folder'
        return redirect(url_for('loggedin', error=error))

    # checking to see where redirect, depending on if there is an item_id
    return redirect(url_for('prodFolders', error=error))


if __name__ == "__main__":
    app.jinja_env.add_extension('jinja2.ext.do')
    app.debug = True
    app.run()




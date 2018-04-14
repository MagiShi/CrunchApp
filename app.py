from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, json, send_file
from flask_mail import Mail, Message
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

app.secret_key = os.environ['SECRET_KEY']

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
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
        itemname = None
        image = None
        itemid = None
        itemidQuery = "SELECT itemid FROM item;"
        itemNameQuery = "SELECT itemname FROM item;"
        imageQuery = "SELECT phfront FROM item;"
        cursor.execute(itemidQuery)
        itemid = cursor.fetchall()
        cursor.execute(itemNameQuery)
        itemname = cursor.fetchall()
        cursor.execute(imageQuery)
        

        return render_template('home.html', itemid=itemid, itemname=itemname, image=image)

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
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
        error = request.args.get('error')
        return render_template('addItem.html', error=error)

# Add item to the database, after button is clicked on add item page.
@app.route('/postaddItem', methods=['POST'])
def addItem():
    if request.form.get("add-item-button"):

        #initialize all values from the html form here (except photos)
        # item_id = request.form.get('barcode')
        item_id = functions.generate_barcode(conn, cursor)
        # print (item_id)

        item_name = request.form.get('itemname')

        # Check this before continuing through everything. All items MUST have an id and name
        if item_name == '':
            error = 'Item must have a name'
            return redirect(url_for('add', error=error))

        description = request.form.get('description')

        prop_t = request.form.get('prop')
        costume_t = request.form.get('costume')
        time_list = request.form.getlist('time')
        culture_list = request.form.getlist('culture')
        sex = request.form.get('gender')
        color_list = request.form.getlist('color')
        size = request.form.get('sizeSelect')
        condition = request.form.get('condition')
        item_type = None
        i_type = None

        # Initialize for photos (Different section just because photos are inserted separately from everything else)
        ph_front = functions.upload_image(request.files.get('photo1'), app.config['UPLOAD_FOLDER'])
        ph_back = functions.upload_image(request.files.get('photo2'), app.config['UPLOAD_FOLDER'])
        ph_top = functions.upload_image(request.files.get('photo3'), app.config['UPLOAD_FOLDER'])
        ph_bottom = functions.upload_image(request.files.get('photo4'), app.config['UPLOAD_FOLDER'])
        ph_left = functions.upload_image(request.files.get('photo5'), app.config['UPLOAD_FOLDER'])
        ph_right = functions.upload_image(request.files.get('photo6'), app.config['UPLOAD_FOLDER'])

        # Initialize itemtype and itype (prop or costume) using prop_t and costume_t
        if prop_t and costume_t:

            # Redirects with error because a prop cannot be both a prop and a costume
            error = 'Item cannot have both a prop type and an costume type'
            return redirect(url_for('add', error=error))
        elif prop_t:
            item_type = 'prop'
            i_type = prop_t
        elif costume_t:
            item_type = 'costume'
            i_type = costume_t

        # Build query string part for color and timeperiod (diff b/c can choose multiple choices and thus mapped to an array)
        color = functions.build_array_query_string(color_list)
        time = functions.build_array_query_string(time_list)
        culture = functions.build_array_query_string(culture_list)

        # String for description
        if description == '':
            description = 'N/A'

        #Build Query string (NOTE: this query does not insert photos (done later) and prod folders (not done during creation))
        char_list = [item_id, item_name, description, item_type, i_type, time, culture, sex, color, size, condition]
        query = "INSERT into item(itemid, itemname, description, itemtype, itype, time, culture, sex, color, size, condition, isavailable, pendingdelete) values ("
        
        for char in char_list:
            if char != None:
                query += "'{0}', ".format(char)
            else:
                query += " NULL, "

        query += " true, false);"
        print (query)

        try: 
            cursor.execute(query)
            conn.commit()

        except Exception as e:
            print (e)
            cursor.execute("rollback;")

            ##If item creation fails
            error = 'Item creation has failed. Make sure that the item name is unique. See Help/Documentation for more details'
            return redirect(url_for('add', error=error))

        # Now insert images for the item, which is already in the database.
        try:
            functions.setImageInDatabase(ph_front, 'phfront', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
            functions.setImageInDatabase(ph_back, 'phback', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
            functions.setImageInDatabase(ph_top, 'phtop', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
            functions.setImageInDatabase(ph_bottom, 'phbottom', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
            functions.setImageInDatabase(ph_right, 'phright', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
            functions.setImageInDatabase(ph_left, 'phleft', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])

        except Exception as e:
            print (e)
            query = "rollback;"
            cursor.execute(query)

            ##If photo insertion fails
            error = 'Item creation failed because of photo insertion. Make sure that added photos do not share the same name'
            query = "DELETE from item where itemid='{0}'".format(item_id)
            cursor.execute(query)
            conn.commit()
            return redirect(url_for('add', error=error))

        error = 'Item successfully added.'
        return redirect(url_for('getItemInfo', item_id=item_id, error=error))


# renders addItem page
@app.route('/help')
def help():
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
        error = request.args.get('error')
        return render_template('help.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/setReservation/<item_id>', methods=["POST", "GET"])
def reserveItem(item_id):
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
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
            # if there is the current reservation. Set default_start to a day after enddate of current reservation.
            if len(current_item_reservation) > 0:
                default_start = current_item_reservation[0][1] + datetime.timedelta(days=1)

            # if there are any future reservations for that item
            if len(future_item_reservations) > 0:
                for c in future_item_reservations:
                    # if startdate of the reservation is same date with default_start, set default_start to a day after enddate of reservation.
                    if c[0] == default_start:
                        default_start = c[1] + datetime.timedelta(days=1)
                    # break the loop at the moment when startdate of the reservation is not as same as default_start.
                    else:
                        break

            default_start = default_start.strftime('%m/%d/%Y')

        except Exception as e:
            cursor.execute("rollback;")
            print(e)
            # if passed_error:
                # error = passed_error
            # else: 
            error = "Cannot retrieve reservation information for item {0}.".format(itemid)
            return render_template('setReservation.html', itemid=item_id, error=error)
        return render_template('setReservation.html', itemid=item_id, all_reservations=all_reservations_this_item, default_start=default_start, error=error)


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
    if start_date <= datetime.datetime.now().date():
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

        except Exception as e:
            cursor.execute("rollback;")
            print(e)

            error = "Cannot retrieve reservation information for item {0}.".format(item_id)
            return render_template('setReservation.html', itemid=item_id, error=error)

        return render_template('setReservation.html', itemid=item_id, all_reservations=all_reservations_this_item, error=passed_error)

    return redirect(url_for('getItemInfo', item_id=itemid, error=error))

@app.route('/editReservation/<path:data>', methods=["POST", "GET"])
def editReservation(data): 

    import ast
    d = ast.literal_eval(data)

    error = None
    email = session.get('user')
    item_id = d.get('itemId')

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
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
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
@app.route('/productions', methods=['POST', 'GET'])
def prodFolders():
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
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

@app.route('/productions/<foldername>', methods=['POST', 'GET'])
def folderContents(foldername):
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
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
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
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
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
        # declare all variables
        error = request.args.get('error')
        item_id = item_id
        item_name = None
        ph_front = None
        ph_back = None
        ph_top = None
        ph_bottom = None
        ph_right = None
        ph_left = None
        description = None
        pending_delete = None
        sex = None
        condition = None
        timep = None
        culture = None
        color = None
        size = None
        item_type = None
        i_type = None
        is_available = None

        start_date = None
        end_date = None
        email = None
        is_reserved=False

        try: 
            # calls functions.py method
            item_name, ph_front, ph_back, ph_top, ph_bottom, ph_right, ph_left, description, pending_delete, sex, condition, timep, culture, color, size, item_type, i_type, is_available = functions.getInfo(item_id, cursor)

            ph_front_data = functions.getImagedata(ph_front)
            ph_back_data = functions.getImagedata(ph_back)
            ph_top_data = functions.getImagedata(ph_top)
            ph_bottom_data = functions.getImagedata(ph_bottom)
            ph_right_data = functions.getImagedata(ph_right)
            ph_left_data = functions.getImagedata(ph_left)

            query = "SELECT startdate, enddate, email FROM reservation WHERE itemid='{0}' and status='current';".format(item_id)
            cursor.execute(query)
            # print (query)
            current_reservation = cursor.fetchone()
            # print(current_reservation)
            if current_reservation != None:

                start_date = str(current_reservation[0])
                end_date = str(current_reservation[1])
                email = current_reservation[2]
                is_reserved = True

            na = ('N/A',)
            if condition[0] is None:
                condition = na
            if sex[0] is None:
                sex = na
            if size[0] is None:
                size = na
            if item_type[0] is None:
                item_type = na
            if i_type[0] is None:
                i_type = na

            photo_count = 0
            if ph_front_data:
                photo_count += 1
            if ph_back_data:
                photo_count += 1
            if ph_top_data:
                photo_count += 1
            if ph_bottom_data:
                photo_count += 1
            if ph_right_data:
                photo_count += 1
            if ph_left_data:
                photo_count += 1

        except Exception as e: 
            print (e)
            cursor.execute("rollback;")

            ##If item does not exist etc
            error = 'Item information cannot be retrieved'
            return redirect(url_for('loggedin', error=error))

        ##culture, color, timeperiod and all ph_*_data are arrays
        return render_template('item.html', itemid=item_id, itemname=item_name, phcount=photo_count, phfront=ph_front_data, phback=ph_back_data, phtop=ph_top_data, phbottom=ph_bottom_data, phright=ph_right_data, phleft=ph_left_data, description=description, delete=pending_delete, sex=sex, condition=condition, timeperiod=timep, culture=culture, color=color, size=size, itemtype=item_type, itype=i_type, isavailable=is_available, error=error, r_start=start_date, r_end=end_date, iscurrentlyreserved=is_reserved, email=email)

# renders editItem page
@app.route('/editItem/<item_id>', methods=["POST", "GET"])
def edit(item_id):
    if functions.isLoggedIn(session.get('user')) is False:
        return redirect(url_for('welcome'))
    else:
        # declare all variables
        error = request.args.get('error')
        item_id = item_id
        item_name = None
        ph_front = None
        ph_back = None
        ph_top = None
        ph_bottom = None
        ph_right = None
        ph_left = None
        description = None
        pending_delete = None
        sex = None
        condition = None
        timep = None
        culture = None
        color = None
        size = None
        item_type = None
        i_type = None
        is_available = None
        
        try: 
            # calls functions.py method
            item_name, ph_front, ph_back, ph_top, ph_bottom, ph_right, ph_left, description, pending_delete, sex, condition, timep, culture, color, size, item_type, i_type, is_available = functions.getInfo(item_id, cursor)

            ph_front_data = functions.getImagedata(ph_front)
            ph_back_data = functions.getImagedata(ph_back)
            ph_top_data = functions.getImagedata(ph_top)
            ph_bottom_data = functions.getImagedata(ph_bottom)
            ph_right_data = functions.getImagedata(ph_right)
            ph_left_data = functions.getImagedata(ph_left)

        except Exception as e: 
            cursor.execute("rollback;")
            print (e)

            ##If item does not exist etc
            error = 'Item information cannot be retrieved for edit'
            return redirect(url_for('loggedin', error=error))

        ##culture, color, timeperiod are arrays/tuples
        ## Passes in  lists for everything except itemname, and description
        return render_template('editItem.html', itemname=item_name[0], itemid=item_id, phfront=ph_front_data, phback=ph_back_data, phtop=ph_top_data, phbottom=ph_bottom_data, phright=ph_right_data, phleft=ph_left_data, description=description[0], delete=pending_delete, sex=sex, condition=condition, timeperiod=timep, culture=culture, color=color, size=size, itemtype=item_type, itype=i_type, error=error)

@app.route('/posteditItem/<item_id>', methods=["POST"])
def editItem(item_id):
    error = request.args.get('error')

    #initialize all values from the html form here (except photos)
    item_id = request.form.get('add-item-button')
    item_name = request.form.get('itemname')

    # Check this before continuing through everything. All items MUST have an id and name
    if item_name == '':
        error = 'Item must have a name'
        return redirect(url_for('edit', error=error, item_id=item_id))

    description = request.form.get('description')

    prop_t = request.form.get('prop')
    costume_t = request.form.get('costume')
    time_list = request.form.getlist('time')
    culture_list = request.form.getlist('culture')
    sex = request.form.get('gender')
    color_list = request.form.getlist('color')
    size = request.form.get('sizeSelect')
    condition = request.form.get('condition')
    item_type = None
    i_type = None

    # Initialize for photos (Different section just because photos are inserted separately from everything else)
    ph_front = functions.upload_image(request.files.get('photo1'), app.config['UPLOAD_FOLDER'])
    ph_back = functions.upload_image(request.files.get('photo2'), app.config['UPLOAD_FOLDER'])
    ph_top = functions.upload_image(request.files.get('photo3'), app.config['UPLOAD_FOLDER'])
    ph_bottom = functions.upload_image(request.files.get('photo4'), app.config['UPLOAD_FOLDER'])
    ph_left = functions.upload_image(request.files.get('photo5'), app.config['UPLOAD_FOLDER'])
    ph_right = functions.upload_image(request.files.get('photo6'), app.config['UPLOAD_FOLDER'])

    # Initialize itemtype and itype (prop or costume) using prop_t and costume_t
    if prop_t and costume_t:
        # Redirects with error because a prop cannot be both a prop and a costume
        error = 'Item cannot have both a prop type and an costume type'
        return redirect(url_for('edit', error=error, item_id=item_id))
    elif prop_t:
        item_type = 'prop'
        i_type = prop_t
    elif costume_t:
        item_type = 'costume'
        i_type = costume_t

    # Build query string part for color and timeperiod (diff b/c can choose multiple choices and thus mapped to an array)
    color = functions.build_array_query_string(color_list)
    time = functions.build_array_query_string(time_list)
    culture = functions.build_array_query_string(culture_list)

    # String for description
    if description == '':
        description = 'N/A'

    #Build Query string (NOTE: this query does not insert photos (done later) and prod folders (not done during creation) as well as itemname and description)
    query = "UPDATE item SET itemtype='{0}', itype='{1}', time='{2}', culture='{3}', sex='{4}', color='{5}', size='{6}', condition='{7}' WHERE itemid='{8}';".format(item_type, i_type, time, culture, sex, color, size, condition, item_id)
    print (query)
    #replace any None with NULL
    query = query.replace('\'None\'', 'NULL')
    print (query)
    # raise NotImplementedError

    try: 
        cursor.execute(query)
        conn.commit()

    except Exception as e:
        print (e)
        cursor.execute("rollback;")

        ##If item creation fails
        error = 'Item editing has failed.'
        return redirect(url_for('edit', error=error, item_id=item_id))

    ##Now change the name and descirption:
    query = "UPDATE item set itemname='{0}', description='{1}'".format(item_name, description)
    print (query)
    try: 
        cursor.execute(query)
        conn.commit()

    except Exception as e:
        print (e)
        cursor.execute("rollback;")

        ##If item creation fails
        error = 'Item name and description cannot be changed. Please make sure that the name is unique. Photos were not updated.'
        return redirect(url_for('edit', error=error, item_id=item_id))

    # Now insert images for the item, which is already in the database.
    try:
        functions.setImageInDatabase(ph_front, 'phfront', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
        functions.setImageInDatabase(ph_back, 'phback', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
        functions.setImageInDatabase(ph_top, 'phtop', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
        functions.setImageInDatabase(ph_bottom, 'phbottom', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
        functions.setImageInDatabase(ph_right, 'phright', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])
        functions.setImageInDatabase(ph_left, 'phleft', item_id, cursor, conn, app.config['UPLOAD_FOLDER'])

    except Exception as e:
        print (e)
        query = "rollback;"
        cursor.execute(query)

        ##If photo insertion fails
        error = 'Photo changes failed. Make sure that added photos do not share the same name. All other information updated.'
        return redirect(url_for('edit', error=error, item_id=item_id))
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



# 
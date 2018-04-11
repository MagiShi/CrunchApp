import base64
from io import BytesIO
import os
from werkzeug.utils import secure_filename

##For Item creation and edit

# Builds a string, converting list to sql array
# Ex: ['c1', 'c2', 'c3'] -> {c1, c2, c3}
def build_array_query_string(char_list):
    length = len(char_list)
    if length > 0:
        char_str = '{'
        for c in range(length):
            if c >= length -1:
                char_str += '{0}'.format(char_list[c])
            else: 
                char_str += '{0}, '.format(char_list[c])
        char_str += '}'
        return char_str
    return None

def upload_image(file, folder):
    if file != None and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(folder, filename))

        print (os.path.join(folder, filename))
    else:
        filename = None

    return filename

def setImageInDatabase(filename, image_col, item_id, cursor, conn, up_folder):
    if filename != None:
        try: 
            print ("looking for file: " + "tmp/"+ filename )
            # print ("loading file")
            f = open("/tmp/" + filename,'rb')
            filedata = f.read()
            f.close()
            # query = "UPDATE item SET {0} = '{1}' WHERE itemid='{2}';".format(image_col, filedata, item_id)
            # cursor.execute(query)
            query = "UPDATE item SET {0} = ".format(image_col, filedata, item_id)
            cursor.execute(query + " %s WHERE itemid=%s;", (filedata, item_id))

            
            conn.commit()
            os.remove(os.path.join(up_folder, filename))
        except Exception as e:
            print (e)
            cursor.execute("rollback;")
            raise e

def getInfo(item_id, cursor):
    cursor.execute("SELECT itemname FROM item WHERE itemid='{0}';".format(item_id))
    itemname = cursor.fetchone()
    cursor.execute("SELECT phfront FROM item WHERE itemid='{0}';".format(item_id))
    ph_front = cursor.fetchone()
    cursor.execute("SELECT phback FROM item WHERE itemid='{0}';".format(item_id))
    ph_back = cursor.fetchone()
    cursor.execute("SELECT phtop FROM item WHERE itemid='{0}';".format(item_id))
    ph_top = cursor.fetchone()
    cursor.execute("SELECT phbottom FROM item WHERE itemid='{0}';".format(item_id))
    ph_bottom = cursor.fetchone()
    cursor.execute("SELECT phright FROM item WHERE itemid='{0}';".format(item_id))
    ph_right = cursor.fetchone()
    cursor.execute("SELECT phleft FROM item WHERE itemid='{0}';".format(item_id))
    ph_left = cursor.fetchone()

    cursor.execute("SELECT description FROM item WHERE itemid='{0}';".format(item_id))
    description = cursor.fetchone()
    cursor.execute("SELECT pendingdelete FROM item WHERE itemid='{0}';".format(item_id))
    pendingdelete = cursor.fetchone()
    cursor.execute("SELECT sex FROM item WHERE itemid='{0}';".format(item_id))
    sex = cursor.fetchone()
    cursor.execute("SELECT condition FROM item WHERE itemid='{0}';".format(item_id))
    condition = cursor.fetchone()
    cursor.execute("SELECT time FROM item WHERE itemid='{0}';".format(item_id))
    timeperiod = cursor.fetchone()
    cursor.execute("SELECT culture FROM item WHERE itemid='{0}';".format(item_id))
    culture = cursor.fetchone()
    cursor.execute("SELECT color FROM item WHERE itemid='{0}';".format(item_id))
    color = cursor.fetchone()
    cursor.execute("SELECT size FROM item WHERE itemid='{0}';".format(item_id))
    size = cursor.fetchone()
    cursor.execute("SELECT itemtype FROM item WHERE itemid='{0}';".format(item_id))
    itemtype = cursor.fetchone()
    cursor.execute("SELECT itype FROM item WHERE itemid='{0}';".format(item_id))
    itype = cursor.fetchone()
    cursor.execute("SELECT isavailable FROM item WHERE itemid='{0}';".format(item_id))
    isavailable = cursor.fetchone()

    return itemname, ph_front, ph_back, ph_top, ph_bottom, ph_right, ph_left, description, pendingdelete, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable

def getImagedata(image):
    if image != None:
        imagedata = []
        image_data = bytes(image)
        encoded = base64.b64encode(image_data)
        stren = encoded.decode("utf-8")
        imagedata.append(stren)
    # to show image as a seperate pop-up (?) --local only
    # data = base64.b64decode(encoded)
    # image1 = Image.open(BytesIO(image_data))
    # image1.show()
        return imagedata
    return None


# def createNewFolder(foldername, cursor, conn):
#     try: 
#         query = "INSERT into folder VALUES ('{0}', false);".format(foldername)
#         cursor.execute(query)
#         conn.commit()
#     except Exception as e: 
#         cursor.execute("rollback;")

#         ##If folder should not have passed checks (should not happen)
#         raise Exception


def updateLastAccess(cursor, conn):
    try:

        #check to see if need to update reservation status. Possibly move to app.py
        cursor.execute("SELECT * from lastaccess WHERE day=CURRENT_DATE;")
        # cursor.execute("SELECT * from lastaccess WHERE day='Mar-03-2018'::date;")
        day = cursor.fetchone()
        # print (day)
        if day == None:
            cursor.execute("UPDATE lastaccess set day=CURRENT_DATE;")
            conn.commit()

            cursor.execute("SELECT CURRENT_DATE;")
            currd = cursor.fetchone()[0]
            # print(currd)

            return True, currd
        return False, day[0]

    except Exception as e:
        cursor.execute("rollback;")
        print(e)

#updates the status column for the reservation table. ('past', 'current', future)
def updateReservationStatus(cursor, conn, day):
    try:
        #flag for whether or not a status was changed to 'past'
        changedpast = False
        cursor.execute("SELECT * from reservation;")
        rlist = cursor.fetchall()
        # print(rlist)
        for email, item, sdate, edate, status in rlist:
            # print (sdate)
            if sdate <= day and edate >= day:
                if status != "current":
                    query = "UPDATE reservation set status='current' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                    print(query)
                    cursor.execute(query)
                    conn.commit()
                print ("current", sdate)
            elif sdate < day :
                if status != "past": 
                    query = "UPDATE reservation set status='past' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                    print(query)
                    cursor.execute(query)
                    conn.commit()
                    changedpast = True
                print ("past", sdate)
            elif edate > day :
                if status != "future":
                    query = "UPDATE reservation set status='future' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                    print(query)
                    cursor.execute(query)
                    conn.commit()
                print ("future", sdate)

        return changedpast

    except Exception as e:
        cursor.execute("rollback;")
        print(e)


# If the # of past reservations for a specific user goes past 3, this function deletes the oldest reservations.
def checkNumOfPastReservations(cursor, conn):
    try:

        # get the number of past reservations each user has
        cursor.execute("SELECT email, count(*) FROM reservation WHERE status='past' GROUP BY email;")
        pastcount = cursor.fetchall()
        # print(pastcount) 
        ## [('a@email.com', 3), ('bb@email.com', 4)]

        #loop through all tuples
        for email, count in pastcount:
            if count > 3:

                # Delete from table if more than 3.  Inner query returns all but the most recent three, which are all deleted.
                query = "DELETE FROM reservation WHERE (email,itemid,startdate) IN (SELECT email, itemid, startdate FROM reservation WHERE email='{0}' ORDER BY enddate DESC OFFSET 3);".format(email)
                cursor.execute(query)
                conn.commit()

    except Exception as e:
        cursor.execute("rollback;")
        print(e)
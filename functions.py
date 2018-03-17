import base64
from io import BytesIO
import os

def getInfo(item_id, cursor):
    cursor.execute("SELECT itemname FROM item WHERE itemid='{0}';".format(item_id))
    itemname = cursor.fetchone()
    cursor.execute("SELECT image1 FROM item WHERE itemid='{0}';".format(item_id))

    image1 = cursor.fetchone()
    cursor.execute("SELECT image2 FROM item WHERE itemid='{0}';".format(item_id))
    image2 = cursor.fetchone()
    cursor.execute("SELECT image3 FROM item WHERE itemid='{0}';".format(item_id))
    image3 = cursor.fetchone()

    cursor.execute("SELECT description FROM item WHERE itemid='{0}';".format(item_id))
    description = cursor.fetchone()
    cursor.execute("SELECT pendingdelete FROM item WHERE itemid='{0}';".format(item_id))
    pendingdelete = cursor.fetchone()
    cursor.execute("SELECT sex FROM item WHERE itemid='{0}';".format(item_id))
    sex = cursor.fetchone()
    # cursor.execute("SELECT condition FROM item WHERE itemid='{0}';".format(item_id))
    # condition = cursor.fetchone()
    # cursor.execute("SELECT timeperiod FROM item WHERE itemid='{0}';".format(item_id))
    # timeperiod = cursor.fetchone()
    # cursor.execute("SELECT culture FROM item WHERE itemid='{0}';".format(item_id))
    # culture = cursor.fetchone()
    cursor.execute("SELECT color FROM item WHERE itemid='{0}';".format(item_id))
    color = cursor.fetchone()
    cursor.execute("SELECT size FROM item WHERE itemid='{0}';".format(item_id))
    size = cursor.fetchone()
    cursor.execute("SELECT itemtype FROM item WHERE itemid='{0}';".format(item_id))
    itemtype = cursor.fetchone()
    # cursor.execute("SELECT itype FROM item WHERE itemid='{0}';".format(item_id))
    # itype = cursor.fetchone()
    cursor.execute("SELECT isavailable FROM item WHERE itemid='{0}';".format(item_id))
    isavailable = cursor.fetchone()

    # return itemname, image1, image2, image3, description, pendingdelete, sex, condition, timeperiod, culture, color, size, itemtype, itype, isavailable
    return itemname, image1, image2, image3, description, pendingdelete, sex, color, size, itemtype, isavailable

def getImagedata(image):
    imagedata = []
    for i in image:
        image_data = bytes(i)
        encoded = base64.b64encode(image_data)
        stren = encoded.decode("utf-8")
        imagedata.append(stren)
    # to show image as a seperate pop-up (?) --local only
    # data = base64.b64decode(encoded)
    # image1 = Image.open(BytesIO(image_data))
    # image1.show()
    return imagedata

def setImageInDatabase(filename, item_id, cursor, conn, up_folder):
    try: 
        print ("looking for file: " + "tmp/"+ filename )
        print ("loading file")
        f = open("/tmp/"+filename,'rb')
        filedata = f.read()
        f.close()
        cursor.execute("UPDATE item SET image1 = %s WHERE itemid=(%s);", (filedata, item_id))
        conn.commit()
        os.remove(os.path.join(up_folder, filename))
    except Exception as e:
        print (e)
        cursor.execute("rollback;")
        raise e

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

def updateReservationStatus(cursor, conn, day):
    try:
        changedpast = False
        cursor.execute("SELECT * from reservation;")
        rlist = cursor.fetchall()
        # print(rlist)
        for email, item, sdate, edate, status in rlist:
            # print (sdate)
            if sdate < day and edate > day and status != "current":
                query = "UPDATE reservation set status='current' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                print(query)
                cursor.execute(query)
                conn.commit()
                # print ("current", sdate)
            elif sdate < day and status != "past": 
                query = "UPDATE reservation set status='past' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                print(query)
                cursor.execute(query)
                conn.commit()
                changedpast = True
                # print ("past", sdate)
            elif edate > day and status != "future":
                query = "UPDATE reservation set status='future' where email='{0}' and itemid='{1}' and startdate='{2}';".format(email, item, sdate)
                print(query)
                cursor.execute(query)
                conn.commit()
                # print ("future", sdate)
            # else:
                ##returns false if nothing changed
                # return False;

        #if return changedpast, this means that we need to check to see that there are only 3 past reservations per user.
        return changedpast

    except Exception as e:
        cursor.execute("rollback;")
        print(e)


# If the # of past resrevations for a specific user goes past 3, this function deletes the oldest reservations.
def checkNumOfPastReservations(cursor, conn):
    try:
        cursor.execute("select email, count(*) from reservation where status='past' group by email;")
        pastcount = cursor.fetchall()
        # print(pastcount)
        for email, count in pastcount:
            if count > 3:
                query = "DELETE FROM reservation WHERE (email,itemid,startdate) IN (SELECT email, itemid, startdate FROM reservation WHERE email='{0}' ORDER BY enddate DESC OFFSET 3);".format(email)
                cursor.execute(query)
                conn.commit()
    except Exception as e:
        cursor.execute("rollback;")
        print(e)
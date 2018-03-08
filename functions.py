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


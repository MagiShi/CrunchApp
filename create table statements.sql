#Create table statements

#Registered User
Create Table registeredUser (email varchar(256) PRIMARY KEY NOT
NULL, username varchar(256) NOT NULL, password varchar(256) NOT NULL,
isAdmin Boolean NOT NULL DEFAULT FALSE );

#item table with add characteristics
Create Table test (itemId varchar(256) PRIMARY KEY NOT NULL, itemName
varchar(256) NOT NULL, image1 BYTEA, image2 BYTEA, image3 BYTEA, pendingDelete Boolean NOT NULL DEFAULT FALSE, description varchar(256), sex sex, condition condition, timeperiod timeperiod, culture culture, color color, size size, itemtype itemtype, itype itype, isAvailable Boolean DEFAULT TRUE);


#Folder
Create Table folder (folderId varchar(256) PRIMARY KEY, folderName
varchar(256));

#ItemInFolder
Create Table iteminfolder(folderId varchar(256) references folder(folderId), itemId varchar(256) references item(itemId), PRIMARY KEY(folderId, itemId));


## Sprint 1&2
-- Create Table registeredUser (email varchar(256) PRIMARY KEY NOT
-- NULL, username varchar(256) NOT NULL, password varchar(256) NOT NULL,
-- isAdmin Boolean NOT NULL DEFAULT FALSE );

-- # table for sprint 2
-- -- Create Table item (itemId varchar(256) PRIMARY KEY NOT NULL, itemName
-- -- varchar(256) NOT NULL, image BYTEA[5], pendingDelete Boolean NOT NULL DEFAULT FALSE, description varchar(256));

-- #item table with add characteristics
-- Create Table item (itemId varchar(256) PRIMARY KEY NOT NULL, itemName
-- varchar(256) NOT NULL, image BYTEA[5], pendingDelete Boolean NOT NULL DEFAULT FALSE, description varchar(256));

-- Create Table reservation ( email varchar(256) NOT NULL references
-- registereduser(email), itemId varchar(256) NOT NULL references
-- item(itemId),  startDate TIMESTAMP NOT NULL, endDate TIMESTAMP NOT NULL,
-- PRIMARY KEY(email, itemId) );

-- Create Table folder (folderId varchar(256) PRIMARY KEY, folderName
-- varchar(256), ownerEmail varchar(256) references
-- registereduser(email));

-- Create Table productInFolder(folderId varchar(256) references
-- folder(folderId), itemId varchar(256) references item(itemId), PRIMARY
-- KEY(folderId, itemId));



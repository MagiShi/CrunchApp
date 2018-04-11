#Create table statements (current)

#Registered User
Create Table registeredUser (email varchar(256) PRIMARY KEY NOT
NULL, username varchar(256) NOT NULL, password varchar(256) NOT NULL, isAdmin Boolean NOT NULL DEFAULT FALSE );

#item table with enum characteristics
Create Table item (itemId varchar(50) PRIMARY KEY NOT NULL, itemName varchar(50) NOT NULL, phfront BYTEA, phback BYTEA, phtop BYTEA, phbottom BYTEA, phleft BYTEA, phright BYTEA, pendingDelete Boolean NOT NULL DEFAULT FALSE, description varchar(256), sex sex, condition condition, time time[], culture culture[], color color[], size size, itemtype itemtype, itype itype, isAvailable Boolean DEFAULT TRUE, f1 Boolean NOT NULL DEFAULT FALSE, f2 Boolean NOT NULL DEFAULT FALSE, f3 Boolean NOT NULL DEFAULT FALSE, folder4 Boolean NOT NULL DEFAULT FALSE, folder5 Boolean NOT NULL DEFAULT FALSE, folder6 Boolean NOT NULL DEFAULT FALSE, folder7 Boolean NOT NULL DEFAULT FALSE, folder8 Boolean NOT NULL DEFAULT FALSE);

#Folder
Create Table folder(folderName varchar(256) PRIMARY KEY, pendingDelete Boolean NOT NULL DEFAULT FALSE);

#Reservation (check enum list for reservationstatus ['past', 'current', 'future'])
#NOTE: startdate and enddate are DATE only, no time. [Ex: 'Mar-01-2018']
Create Table reservation (email varchar(256) NOT NULL references registereduser(email), itemId varchar(256) NOT NULL references item(itemId),  startDate DATE NOT NULL, endDate DATE NOT NULL, status reservationstatus NOT NULL, PRIMARY KEY(email, itemId, startDate) );

# Should only have one row, this is used as a flag to decide whether
# or not to recreate a view for reservation (curr, past, futre)
Create Table lastaccess (day DATE PRIMARY KEY);

#List of production folders:
Create Table productionfolders(folderName varchar(256) NOT NULL, folderId folderId UNIQUE, PRIMARY KEY(folderId));


## Sprint 4
-- #ItemInFolder
-- Create Table iteminfolder(folderName varchar(256) references folder(folderName), itemId varchar(256) references item(itemId), PRIMARY KEY(folderName, itemId));


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



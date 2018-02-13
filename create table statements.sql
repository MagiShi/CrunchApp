#Create table statements
Create Table registeredUser (email varchar(256) PRIMARY KEY NOT
NULL, username varchar(256) NOT NULL, password varchar(256) NOT NULL,
isAdmin Boolean NOT NULL DEFAULT FALSE );

Create Table item (itemId varchar(256) PRIMARY KEY NOT NULL, itemName
varchar(256) NOT NULL, image BYTEA[5], pendingDelete Boolean NOT NULL DEFAULT FALSE, description varchar(256));

Create Table temptable(itemId varchar(256) PRIMARY KEY NOT NULL, name varchar(256), image BYTEA[5]);

Create Table reservation ( email varchar(256) NOT NULL references
registereduser(email), itemId varchar(256) NOT NULL references
item(itemId),  startDate TIMESTAMP NOT NULL, endDate TIMESTAMP NOT NULL,
PRIMARY KEY(email, itemId) );

Create Table folder (folderId varchar(256) PRIMARY KEY, folderName
varchar(256), ownerEmail varchar(256) references
registereduser(email));

Create Table productInFolder(folderId varchar(256) references
folder(folderId), itemId varchar(256) references item(itemId), PRIMARY
KEY(folderId, itemId));

#Mock data
Insert into registereduser values ('a@email.com', 'admin', 'pw',
TRUE);
Insert into registereduser (email, username, password, isAdmin) values
('student@email.com', 'student1', 'stu', FALSE), ('bb@email.com',
'bb', 'pwbb', FALSE), ('cc@email.com', 'cc', 'pwcc', FALSE);
Insert into item(itemId, itemName, image, pendingDelete, description) values ('1', 'One', NULL, FALSE, 'thing one'), ('2', 'Two', NULL, FALSE, 'thing two'); 
Insert into item(itemId, itemName, image, pendingDelete, description) values ('21', 'One', '{"23423", "4354"}', FALSE, 'thing one'), ('22', 'Two', '{"2342"}', FALSE, 'thing two');

Insert into reservation values ('a@email.com', '1', '2011-05-16 15:36:38',
'2011-05-16 15:36:38');
Insert into folder values ('F1', 'Folder1', 'student@email.com');
Insert into productInFolder values ('F1', '1');

#SQL for mock login/registration
Insert into registereduser values ('a@email.com', 'admin', 'pw',
TRUE);
Select password from registereduser where username ='admin';

#Drop table statements
DROP table folder;
DROP table productInFolder;
DROP table reservation;
DROP table item;
DROP table registereduser;

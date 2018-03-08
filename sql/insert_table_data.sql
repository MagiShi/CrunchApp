#Mock data for testing
#User
Insert into registereduser values ('a@email.com', 'admin', 'pw', TRUE);
Insert into registereduser (email, username, password, isAdmin) values ('student@email.com', 'student1', 'stu', FALSE), ('bb@email.com', 'bb', 'pwbb', FALSE), ('cc@email.com', 'cc', 'pwcc', FALSE);

#Item (without image)
Insert into item (itemId, itemName, pendingDelete, description, sex, condition, timeperiod, color, size, itemtype, isAvailable) 
values ('item1', 'b_item1', false, 'item1 no picture', 'unisex', 'good', '{classical}', '{red}', 's', 'costume', true ), 
('item2', 'b_item2', false, 'item2 no picture', 'male', 'good', '{other}', '{red, orange, green}', 's', 'costume', true )
;


#Folder
Insert into folder values ('name1', false), ('name2', false);


-- ## These are all for sprint 1 & 2, because of table changes, see sprint 3, to be added above.
-- Insert into registereduser values ('a@email.com', 'admin', 'pw',
-- TRUE);
-- Insert into registereduser (email, username, password, isAdmin) values
-- ('student@email.com', 'student1', 'stu', FALSE), ('bb@email.com',
-- 'bb', 'pwbb', FALSE), ('cc@email.com', 'cc', 'pwcc', FALSE);
-- Insert into item(itemId, itemName, image, pendingDelete, description) values ('1', 'One', NULL, FALSE, 'thing one'), ('2', 'Two', NULL, FALSE, 'thing two'); 
-- Insert into item(itemId, itemName, image, pendingDelete, description) values ('21', 'One', '{"23423", "4354"}', FALSE, 'thing one'), ('22', 'Two', '{"2342"}', FALSE, 'thing two');

-- Insert into reservation values ('a@email.com', '1', '2011-05-16 15:36:38',
-- '2011-05-16 15:36:38');
-- Insert into folder values ('F1', 'Folder1', 'student@email.com');
-- Insert into productInFolder values ('F1', '1');

-- #SQL for mock login/registration
-- Insert into registereduser values ('a@email.com', 'admin', 'pw',
-- TRUE);
-- Select password from registereduser where username ='admin';



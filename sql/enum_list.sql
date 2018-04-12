##ENUMS for characteristics:
CREATE TYPE SEX AS ENUM ('male', 'female', 'unisex');
CREATE TYPE CONDITION AS ENUM('new', 'good', 'used', 'poor');
CREATE TYPE TIME AS ENUM('ancient', 'classical', 'earlymodern', 'latemodern', '20th', '21st', 'future', 'other');
CREATE TYPE CULTURE AS ENUM('namerica', 'samerica', 'asia', 'europe', 'africa', 'australia', 'fantasy', 'scifi', 'other');
CREATE TYPE COLOR AS ENUM('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'white', 'black', 'other');
CREATE TYPE SIZE AS ENUM('xxs', 'xs', 's', 'm', 'l', 'xl', 'xxl', 'other');
CREATE TYPE ITEMTYPE AS ENUM('prop', 'costume');
CREATE TYPE ITYPE AS ENUM('outerwear', 'tops', 'pants', 'skirt', 'dress', 'underwear', 'footwear', 'other', 'hand', 'personal', 'set', 'trims', 'setdressing', 'greens', 'fx');

#ENUM for reservation status
CREATE TYPE reservationstatus AS ENUM ('past', 'current', 'future');

#ENUM for productionFolderId
CREATE TYPE folderId AS ENUM('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8');

#EX: To see enums for size:
select enumlabel from pg_enum where enumtypid = 'size'::regtype;
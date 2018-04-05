##ENUMS for characteristics:
CREATE TYPE SEX AS ENUM ('male', 'female', 'unisex');
CREATE TYPE CONDITION AS ENUM('new', 'good', 'used', 'poor');
CREATE TYPE TIMEPERIOD AS ENUM('ancient', 'classical', 'earlymodern', 'latemodern', '20th', '21st', 'future', 'other');
CREATE TYPE CULTURE AS ENUM('northamerican', 'southamerican', 'asian', 'european', 'african', 'australian', 'other');
CREATE TYPE COLOR AS ENUM('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'white', 'black', 'other');
CREATE TYPE SIZE AS ENUM('xxs', 'xs', 's', 'm', 'l', 'xl', 'xxl', 'other');
CREATE TYPE ITEMTYPE AS ENUM('prop', 'costume');
CREATE TYPE ITYPE AS ENUM('outer', 'top', 'pants', 'skirts', 'dress', 'under', 'footwear', 'other', 'hand', 'personal', 'set', 'trim', 'setdressing', 'greens', 'mfx');

#ENUM for reservation status
CREATE TYPE reservationstatus AS ENUM ('past', 'current', 'future');

#EX: To see enums for size:
-- select enumlabel from pg_enum where enumtypid = 'size'::regtype;
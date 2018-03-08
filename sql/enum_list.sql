##ENUMS for characteristics:
CREATE TYPE SEX AS ENUM ('male', 'female', 'unisex');
CREATE TYPE CONDITION AS ENUM('new', 'good', 'used', 'poor');
CREATE TYPE TIMEPERIOD AS ENUM('ancient', 'classical', 'earlymodern', 'latemodern', 'contemporary', 'future', 'other');
CREATE TYPE CULTURE AS ENUM('northamerican', 'southamerican', 'asian', 'european', 'african', 'australian', 'other');
CREATE TYPE COLOR AS ENUM('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'white', 'black');
CREATE TYPE SIZE AS ENUM('xxs', 'xs', 's', 'm', 'l', 'xl', 'xxl');
CREATE TYPE ITEMTYPE AS ENUM('prop', 'costume');
CREATE TYPE ITYPE AS ENUM('outer', 'top', 'pants', 'skirts', 'dress', 'under', 'footwear', 'other', 'hand', 'personal', 'set', 'trim', 'setdressing', 'greens', 'mfx');

#EX: To see enums for size:
-- select enumlabel from pg_enum where enumtypid = 'size'::regtype;
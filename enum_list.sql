##ENUMS for characteristics:
CREATE TYPE SEX AS ENUM ('male', 'female', 'unisex');
CREATE TYPE CONDITION AS ENUM('new', 'good', 'used', 'poor');
CREATE TYPE TIMEPERIOD AS ENUM('ancient', 'postclassical', 'earlymodern', 'latemodern', 'contemporary', 'future', 'other');
CREATE TYPE CULTURE AS ENUM('northamerican', 'southamerican', 'asian', 'european', 'african', 'australian', 'other');
CREATE TYPE COLOR AS ENUM('red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'white', 'black');
CREATE TYPE SIZE AS ENUM('lxs', 'xs', 's', 'm', 'l', 'xl', 'mxl');
CREATE TYPE ITEMTYPE AS ENUM('prop', 'costume');
CREATE TYPE ITYPE AS ENUM('outer', 'top', 'pants', 'skirts', 'dress', 'under', 'footwear', 'other', 'hand', 'personal', 'set', 'trim', 'setdressing', 'greens', 'mfx');
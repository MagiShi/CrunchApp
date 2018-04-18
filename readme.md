# Thracker Documentation

# 1. Release Notes
### Software Features
- **Adding items**
  - Users can save items along with defining characteristics into the application.
  - Characteristics include: prop/costume type, color, size, time period
- **Production Folders**
  - Items can be organized into one or more theater productions, represented as "production folders" in the application.
- **Search and filter**
  - Users can search for specific items by typing in the item name or unique barcode into the search bar.
  - For a less specific search, users can narrow down the entire database of items by choosing characteristics to filter by. 
- **Reservations**
  - Users can mark items as to be reserved for a certain date range. This way, other users know that the item is unavailable during that time.
  - Users can view their upcoming, current, and past reservations.
### Bugs and Defects
- When making or updating the date range of a reservation, the calendar widget requires that you **press the green Apply button** for the input to save. (Do not choose the date and then click outside of the calendar widget if you want changes to be saved.)
- On an item's detail page, if there is a carousel of images and the user clicks through the carousel, the image only resizes and repositions itself after a second or two. This is just a minor aesthetic bug.
- Another minor aesthetic bug: some of the icons on the navigation bar (search bar and the two menu buttons) take some time to load. This makes the buttons smaller for a moment or so.
### Missing Functionality
- Feature 1
- Feature 2

# 2. Install Guide
### Pre-requisites
- Machine should have Python installed
### Dependent libraries
- requirements.txt
- Set up [Flask](http://flask.pocoo.org/docs/0.12/quickstart/)
- Set up [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
### Download instructions
- You can find the source code for Thracker at this [repo](https://github.com/MagiShi/CrunchApp).
### Installation of application
- Thracker is a web application and will not require installation for use.
### Run instructions
- Navigate to the program files
- `heroku open` will open the herokuapp project
- `flask run` will open the application locally
### Troubleshooting
- Sometimes a user's reservations will not appear on their My Reservations page. Our highly technical fix is just to refresh until they eventually appear.
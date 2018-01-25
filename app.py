from flask import Flask, flash, redirect, render_template, request, session, abort
 
app = Flask(__name__)
 
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login.html')
def returningUser():
    return render_template('login.html')

@app.route('/home.html')
def login():
    return render_template('home.html')
def guest():
    # should look different than a registered user (not able to add, delete, etc)
    return render_template('home.html')

@app.route('/register.html')
def newUser():
    return render_template('register.html')
def register():
    return render_template('home.html')

@app.route('/addItem.html')
def add():
    return render_template('addItem.html')

if __name__ == "__main__":
    app.run()
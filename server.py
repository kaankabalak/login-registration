from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5 # imports the md5 module to generate a hash

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app,'logindb')
@app.route('/')
def index():
    return render_template('index.html') # pass data to our template

@app.route('/success')
def success():
    query = "SELECT * FROM users"                           # define your query
    users = mysql.query_db(query)                           # run query with query_db()
    return render_template('success.html', all_users=users) # pass data to our template

@app.route('/register', methods=['POST'])
def register():
    isFormValid = True
    if len(request.form['email']) < 1:
        flash("Email cannot be empty")
        isFormValid = False
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Email should be valid")
        isFormValid = False

    if len(request.form['first_name']) < 2:
        flash("First name should be at least 2 characters")
        isFormValid = False

    if len(request.form['last_name']) < 2:
        flash("Last name should be at least 2 characters")
        isFormValid = False

    if len(request.form['password']) < 1:
        flash("Password cannot be empty")
        isFormValid = False
    elif len(request.form['password']) > 8:
        flash("Password cannot be more than 8 characters!")
        isFormValid = False
    elif md5.new(request.form['password']).hexdigest() != md5.new(request.form['confirmpw']).hexdigest():
        flash("Password and password confirmation should match")
        isFormValid = False

    if isFormValid:
        flash("Thanks for submitting your information")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'password': md5.new(request.form['password']).hexdigest()
               }
        # Run query, with dictionary values injected into the query.
        session['name'] = request.form['first_name']
        mysql.query_db(query, data)
        return redirect('/success')
    else:
        return redirect('/')
@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email = :specific_email"                           # define your query
    data = {
            'specific_email': request.form['email'],
            'password': request.form['password']
            }
    user = mysql.query_db(query, data)                           # run query with query_db()
    if(md5.new(request.form['password']).hexdigest() == user[0]['password']):
        session['name'] = user[0]['first_name']
        return redirect('/success')
    else:
        flash("The password you have entered is incorrect")
        return redirect('/')

app.run(debug=True)

from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app,'emaildb')
@app.route('/')
def index():
    return render_template('index.html') # pass data to our template

@app.route('/success')
def success():
    query = "SELECT * FROM emails"                           # define your query
    emails = mysql.query_db(query)                           # run query with query_db()
    return render_template('success.html', all_emails=emails) # pass data to our template

@app.route('/submit', methods=['POST'])
def submit():
    if len(request.form['address']) < 1:
        flash("Email cannot be empty")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['address']):
        flash("Email should be valid")
        return redirect('/')
    else:
        flash("The email address you have entered (" + request.form['address'] + ") is a valid email address! Thank you!")
        # Write query as a string. Notice how we have multiple values
        # we want to insert into our query.
        query = "INSERT INTO emails (address, created_at, updated_at) VALUES (:address, NOW(), NOW())"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                 'address': request.form['address']
               }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)
        return redirect('/success')
    
app.run(debug=True)

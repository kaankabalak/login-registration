from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5 # imports the md5 module to generate a hash

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector(app,'walldb')
@app.route('/')
def index():
    return render_template('index.html') # pass data to our template

@app.route('/wall')
def wall():
    query = "SELECT messages.id AS messageid, message, first_name, last_name, messages.created_at FROM messages JOIN users ON users.id = messages.user_id ORDER BY messages.created_at"                           # define your query
    messages = mysql.query_db(query)                           # run query with query_db()

    query1 = "SELECT comments.id, comments.message_id, comment, first_name, last_name, comments.created_at FROM comments JOIN users ON users.id = comments.user_id ORDER BY comments.created_at"                           # define your query
    comments = mysql.query_db(query1)                           # run query with query_db()

    return render_template('wall.html', all_messages=messages, all_comments=comments) # pass data to our template

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
        mysql.query_db(query, data)
        query = "SELECT * FROM users WHERE email = :specific_email"                           # define your query
        data = {
                'specific_email': request.form['email'],
                }
        user = mysql.query_db(query, data)  
        session['name'] = user[0]['first_name']
        session['user_id'] = user[0]['id']
        return redirect('/wall')
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email = :specific_email"                           # define your query
    data = {
            'specific_email': request.form['email']
            }
    user = mysql.query_db(query, data)                           # run query with query_db()
    if(md5.new(request.form['password']).hexdigest() == user[0]['password']):
        session['name'] = user[0]['first_name']
        session['user_id'] = user[0]['id']
        return redirect('/wall')
    else:
        flash("The password you have entered is incorrect")
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('name')
    session.pop('user_id')
    return redirect('/')

@app.route('/send', methods=['POST'])
def send():
    query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES (:message, :user_id, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
            'message': request.form['message'],
            'user_id': session['user_id']
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/comment', methods=['POST'])
def comment():
    query = "INSERT INTO comments (comment, message_id, user_id, created_at, updated_at) VALUES (:comment, :message_id, :user_id, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
            'comment': request.form['comment'],
            'user_id': session['user_id'],
            'message_id': request.form['messageid']
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    return redirect('/wall')

app.run(debug=True)

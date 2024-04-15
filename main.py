from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json






from flask_session import Session
import pyodbc


with open('config.json','r') as c:
    params=json.load(c)["params"]
    
    
local_server=True
app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["gmail-user"],
    MAIL_PASSWORD=params["gmail-password"]
)
mail = Mail(app)

if (local_server):
  app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
     app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']  
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80),  nullable=False)
    Email = db.Column(db.String(50),  nullable=False)
    Phone_num = db.Column(db.String(12),  nullable=False)
    date = db.Column(db.String(12),  nullable=True)
    mes = db.Column(db.String(120),  nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),  nullable=False)
    slug = db.Column(db.String(21),  nullable=False)
    content= db.Column(db.String(120),  nullable=False)
    date = db.Column(db.String(12),  nullable=True)
    



app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'your_prefix'

Session(app)

conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=DEWANSH;'
    'Database=master;'
    'Trusted_Connection=yes;'
    'autocommit=True'
)
cursor = conn.cursor()
cursor.execute("use flask_project;")

@app.route("/")
def index():
    username = session.get('username')
    if username:
        print(username)
        return render_template("index.html")
    else:
        return redirect(url_for('login'))

@app.route('/end_session')
def end_session():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/post')
def post():
    return render_template("post.html")

@app.route('/contact', methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        '''ADD ENTRY TO DATABASE'''
        name =request.form.get('name')
        email =request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        
        entry = Contacts(Name=name, Phone_num=phone, mes=message, date=datetime.now() , Email=email)

        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from Blog' , sender = email , recipients=[params['gmail-user']] , body = message +"\n" + phone )
        
          
       
        
        
    
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute("SELECT * FROM userinfo WHERE name=? AND password=?", username, password)
        ans = cursor.fetchall()
        if ans:
            session.clear()
            session['username'] = username
            session['message'] = f"Login confirmed! Welcome, {username}!"
            return redirect(url_for('index', message=message))
        else:
            message = "No existing user found. Please sign up."
            return render_template("signup.html", message=message)

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("name")
        pwd = request.form.get("password")
        email = request.form.get("email")
        confirm_pwd = request.form.get("confirm_password")
        print(username, pwd, email, confirm_pwd)
        if pwd == confirm_pwd:
            print("pwd same")
            cursor.execute("INSERT INTO UserInfo (name, password, email) VALUES (?, ?, ?)", username, pwd, email)
            conn.commit()
            try:
                table = f"{username}_order"
                cursor.execute(f"CREATE TABLE {table} (order_datetime DATETIME, order_details TEXT);")
                conn.commit()
            except Exception as e:
                print(f"Error creating table: {e}")
            session.clear()
            return render_template("login.html")

    return render_template("signup.html")

@app.route("/article1")
def article1():
    return render_template("article1.html")

@app.route("/olderpost")
def olderpost():
    return render_template("index2.html")

@app.route("/article2")
def ret_article2():
    return render_template("article2.html")

@app.route("/article3")
def ret_article3():
    return render_template("article3.html")

@app.route("/article4")
def ret_article4():
    return render_template("article4.html")

@app.route("/addblog", methods=["GET", "POST"])
def addblog():
    if request.method == "POST":
        # Get the form data
        title = request.form["blog-title"]
        author = request.form["blog-author"]
        content = request.form["blog-content"]

        # Process the form data: Insert into the database
        cursor.execute("INSERT INTO BlogPosts (title, author, date, content) VALUES (?, ?, ?, ?);", (title, author, datetime.now(), content))
        conn.commit()

        # Redirect to a success page or to the addblog page
        return redirect(url_for("addblog"))
    else:
        return render_template("AddBlog.html")

@app.route('/article/<string:post_slug>', methods=['GET'])
def post_details(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post)



if __name__ == '__main__':
    app.run(debug=True)

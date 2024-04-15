import pyodbc
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=DEWANSH;'
    'Database=master;'
    'Trusted_Connection=yes;'
    'autocommit=True'
)
cursor = conn.cursor()
cursor.execute("use flask_project;")
cursor.execute(f"INSERT INTO UserInfo (name, password, email)VALUES (?, ?, ?);", 'Dewansh', '124','Dewansh@gamil.com')
conn.commit()

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute(f"select * from userinfo where name=? and password=?;", username, password)
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
            cursor.execute(f"INSERT INTO UserInfo (name, password, email)VALUES (?, ?, ?);", username, pwd, email)
            conn.commit()
            try:
                table = f"{username}_order"
                cursor.execute(f"CREATE TABLE {table} (order_datetime DATETIME, order_details TEXT);")
                conn.commit()
            except Exception as e:
                print(f"Error creating table: {e}")
            session.clear()
            render_template("login.html")

    return render_template("signup.html")

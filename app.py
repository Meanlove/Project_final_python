from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = "123456"


def connect_db():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_python',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except:
        print("Database connection failed")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return "Email already registered!"

        cursor.execute("INSERT INTO users (username,email,password,role) VALUES (%s,%s,%s,%s)",
            (username, email, password, role)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        if user:

            if user["password"] == password and user["role"] == role:

                session["id"] = user["id"]
                session["role"] = user["role"]

                if user["role"] == "Admin":
                    return redirect(url_for("adminpage"))
                else:
                    return redirect(url_for("userpage"))

        return "Login failed! Wrong credentials."

    return render_template("index.html")


@app.route("/userpage")
def userpage():

    if "id" not in session or session["role"] != "Customer":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("user_page.html", user=user)


@app.route("/adminpage")
def adminpage():

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin_page.html", admin=admin)


@app.route("/products")
def products():

    return render_template("products.html", products=products)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    print("Server is running...")
    app.run(debug=True)
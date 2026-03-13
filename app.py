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

    return render_template("User.html", user=user)


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


@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template("contact.html")

# =========== Admin ==============

products = [
    {"name": "MacBook Pro", "price": 1999, "image_url": "https://picsum.photos/300/200"},
    {"name": "iPhone 15", "price": 999, "image_url": "https://picsum.photos/301/200"},
]
@app.route('/admin')
def admin_page():
    return render_template('admin_dashboard.html', total_products=len(products))

@app.route('/admin/products')
def admin_products():
    return render_template('admin_products.html', products=products)

@app.route('/admin/add-product', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        old_price = request.form['old_price']
        stock = request.form['stock']
        # image handling skipped for simplicity
        image_url = "https://picsum.photos/300/200"
        products.append({"name": name, "price": price, "image_url": image_url})
        return redirect(url_for('admin_products'))
    return render_template('add_product.html')








# @app.route("/add_product", methods=["POST"])
# def add_product():
#     connection = connect_db()
#     cursor = connection.cursor()
#     name = request.form["name"]
#     brand = request.form["brand"]
#     category = request.form["category"]
#     price = request.form["price"]
#     old_price = request.form["old_price"]
#     stock = request.form["stock"]
#     status = request.form["status"]
#     badge = request.form["badge"]
#     starts = request.form["starts"]
#     reviews = request.form["reviews"]
    
#     file = request.files["image"]
#     if file:
#         image_path = "static/uploads/" + file.filename
#         file.save(image_path)
#         cursor.execute("INSERT INTO products2 (name, brand, category, price, old_price, stocks, status, badge, starts, img, reviews) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
#             (name, brand, category, price, old_price, stock, status, badge, starts, image_path, reviews)
#         )
#         connection.commit()
#         cursor.close()
#         connection.close()

    
#     return render_template("admin_page.html")

if __name__ == "__main__":
    print("Server is running...")
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session,flash
import pymysql
import uuid
import os
import pymysql.cursors

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


def get_products():
    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products2")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


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

        cursor.execute(
            "INSERT INTO users (username,email,password,role) VALUES (%s,%s,%s,%s)",
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
        cursor.close()
        conn.close()

        if user and user["password"] == password and user["role"] == role:
            session["id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "Admin":
                return redirect(url_for("admin_dashboard"))
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

    products = get_products()
    return render_template("User.html", user=user, products=products)


@app.route("/adminpage")
def adminpage():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))
    return redirect(url_for("admin_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # You can save to DB or send email here
        name    = request.form.get('name')
        email   = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template("contact.html")


@app.route("/products")
def products_page():
    products = get_products()
    return render_template("products.html", products=products)


# =========== Admin ==============

@app.route('/admin')
def admin_dashboard():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    total_products = len(get_products())
    return render_template('admin_dashboard.html', admin=admin, total_products=total_products)


@app.route('/admin/products')
def admin_products():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    products = get_products()
    return render_template("admin_products.html", products=products, admin=admin)


@app.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()

    if request.method == 'POST':
        name        = request.form['name']
        price       = request.form['price']
        old_price   = request.form.get('old_price', None)
        stock       = request.form['stock']
        category    = request.form.get('category', '')
        description = request.form.get('description', '')
        file        = request.files['image']

        filename = ""
        if file and file.filename != "":
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute(
            """INSERT INTO products2
               (name, price, old_price, stock, img, category, description)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (name, price, old_price, stock, filename, category, description)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_products'))

    cursor.close()
    conn.close()
    return render_template('add_product.html', admin=admin)


@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()

    if request.method == 'POST':
        name        = request.form['name']
        price       = request.form['price']
        old_price   = request.form.get('old_price', None)
        stock       = request.form['stock']
        category    = request.form.get('category', '')
        description = request.form.get('description', '')
        file        = request.files.get('image')

        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute(
                """UPDATE products2 SET name=%s, price=%s, old_price=%s,
                   stock=%s, category=%s, description=%s, img=%s WHERE id=%s""",
                (name, price, old_price, stock, category, description, filename, product_id)
            )
        else:
            cursor.execute(
                """UPDATE products2 SET name=%s, price=%s, old_price=%s,
                   stock=%s, category=%s, description=%s WHERE id=%s""",
                (name, price, old_price, stock, category, description, product_id)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin_products'))

    cursor.execute("SELECT * FROM products2 WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_product.html', product=product, admin=admin)


@app.route('/admin/delete-product/<int:product_id>')
def delete_product(product_id):
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products2 WHERE id=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_products'))
    
    




# ========  admin account ============

@app.route('/admin/profile')
def admin_profile():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session["id"],))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    total_products = len(get_products())
    return render_template('admin_profile.html', admin=admin, total_products=total_products)


@app.route('/admin/profile/edit', methods=['POST'])
def admin_profile_edit():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    username         = request.form['username']
    email            = request.form['email']
    phone_code       = request.form.get('phone_code', '')
    phone            = request.form.get('phone', '')
    new_password     = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # ── Handle profile image upload ──
    profile_img = None
    file = request.files.get('profile_img')
    if file and file.filename != '':
        ext = os.path.splitext(file.filename)[1]
        filename = 'admin_' + str(uuid.uuid4()) + ext
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        profile_img = filename

    # ── Build query depending on what changed ──
    if new_password:
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('admin_profile'))

        if profile_img:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, phone_code=%s, phone=%s, password=%s, profile_img=%s WHERE id=%s",
                (username, email, phone_code, phone, new_password, profile_img, session["id"])
            )
        else:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, phone_code=%s, phone=%s, password=%s WHERE id=%s",
                (username, email, phone_code, phone, new_password, session["id"])
            )
    else:
        if profile_img:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, phone_code=%s, phone=%s, profile_img=%s WHERE id=%s",
                (username, email, phone_code, phone, profile_img, session["id"])
            )
        else:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s, phone_code=%s, phone=%s WHERE id=%s",
                (username, email, phone_code, phone, session["id"])
            )

    conn.commit()
    cursor.close()
    conn.close()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('admin_profile'))


@app.route('/admin/delete-account')
def admin_delete_account():
    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (session["id"],))
    conn.commit()
    cursor.close()
    conn.close()
    session.clear()
    return redirect(url_for('login'))



if __name__ == "__main__":
    print("Server is running...")
    app.run(debug=True)
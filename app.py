from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector as mysql
from functools import wraps

app = Flask(__name__)
app.secret_key = "mysecretkey"


# ---------------- DB CONNECTION ----------------
def get_db():
    con = mysql.connect(
        host="sql3.freesqldatabase.com",
        user="sql3816537",
        password="564d2rpRvh",
        database="sql3816537"
    )
    return con, con.cursor(dictionary=True)


# ---------------- LOGIN REQUIRED ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="All fields required")

        con, cur = get_db()
        cur.execute(
            "select * from users where username=%s and password=%s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        con.close()

        if user:
            session["user"] = username
            return redirect(url_for("data"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("register.html", error="All fields required")

        try:
            con, cur = get_db()
            cur.execute(
                "insert into users (username, password) values (%s, %s)",
                (username, password)
            )
            con.commit()
            cur.close()
            con.close()
            return redirect(url_for("login"))
        except:
            return render_template("register.html", error="Username already exists")

    return render_template("register.html")


# ---------------- STUDENT LIST ----------------
@app.route("/data")
@login_required
def data():
    con, cur = get_db()
    cur.execute("select id, name, age, course from students")
    students = cur.fetchall()
    cur.close()
    con.close()

    return render_template("data.html", students=students)


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")

        if not name or not age or not course:
            return render_template("add_student.html", error="All fields required")

        if int(age) <= 0:
            return render_template("add_student.html", error="Invalid age")

        con, cur = get_db()
        cur.execute(
            "insert into students (name, age, course) values (%s, %s, %s)",
            (name, age, course)
        )
        con.commit()
        cur.close()
        con.close()

        return redirect(url_for("data"))

    return render_template("add_student.html")


# ---------------- EDIT STUDENT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):
    con, cur = get_db()

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")

        if not name or not age or not course:
            cur.execute("select * from students where id=%s", (id,))
            student = cur.fetchone()
            cur.close()
            con.close()
            return render_template(
                "edit_student.html",
                student=student,
                error="All fields required"
            )

        if int(age) <= 0:
            cur.execute("select * from students where id=%s", (id,))
            student = cur.fetchone()
            cur.close()
            con.close()
            return render_template(
                "edit_student.html",
                student=student,
                error="Invalid age"
            )

        cur.execute(
            "update students set name=%s, age=%s, course=%s where id=%s",
            (name, age, course, id)
        )
        con.commit()
        cur.close()
        con.close()

        return redirect(url_for("data"))

    cur.execute("select * from students where id=%s", (id,))
    student = cur.fetchone()
    cur.close()
    con.close()

    return render_template("edit_student.html", student=student)


# ---------------- DELETE STUDENT ----------------
@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):
    con, cur = get_db()
    cur.execute("delete from students where id=%s", (id,))
    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("data"))


# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
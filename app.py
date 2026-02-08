from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector as mysql

app = Flask(__name__)
app.secret_key = "mysecretkey"

con = mysql.connect(
    host="sql3.freesqldatabase.com",
    user="sql3816537",
    password="564d2rpRvh",
    database="sql3816537"
)

cur = con.cursor()

@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        query = "select * from users where username=%s and password=%s"
        cur.execute(query, (username, password))
        user = cur.fetchone()

        if user:
            session["user"] = username
            return redirect(url_for("data"))
        else:
            return "Invalid username or password"

    return render_template("login.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        query = "insert into users (username, password) values (%s, %s)"
        cur.execute(query, (username, password))
        con.commit()

        return redirect(url_for("login"))
    return render_template("register.html")



@app.route("/data")
def data():
    if "user" not in session:
        return redirect(url_for("login"))

    query = "select id, name, age, course from students"
    cur.execute(query)
    students = cur.fetchall()

    return render_template(
        "data.html",
        username=session["user"],
        students=students
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")

        query = "insert into students (name, age, course) values (%s, %s, %s)"
        cur.execute(query, (name, age, course))
        con.commit()

        return redirect(url_for("data"))

    return render_template("add_student.html")



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")

        query = "update students set name=%s, age=%s, course=%s where id=%s"
        cur.execute(query, (name, age, course, id))
        con.commit()

        return redirect(url_for("data"))
   
    query = "select id, name, age, course from students where id=%s"
    cur.execute(query, (id,))
    student = cur.fetchone()

    return render_template("edit_student.html", student=student)


@app.route("/delete/<int:id>")
def delete_student(id):
    if "user" not in session:
        return redirect(url_for("login"))

    query = "delete from students where id=%s"
    cur.execute(query, (id,))
    con.commit()

    return redirect(url_for("data"))


if __name__ == "__main__":
    app.run(debug=True)

    
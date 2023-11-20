from phongkham_app import app
from flask import render_template


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=['get', 'post'])
def user_register():
    return render_template("register.html")


@app.route("/login", methods=['get', 'post'])
def user_login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask

app = Flask("__name__")


@app.route("/")
def home():
    return "Hello Worlds!!!"


@app.route("/test")
def test():
    return "Dat lich kham ngay!!!"


if __name__ == "__main__":
    app.run(debug=True)

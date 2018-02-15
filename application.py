from flask import Flask, jsonify, render_template, request
from flask_mail import Mail, Message
import os
import sqlite3

# Configure application
app = Flask(__name__)

# Configure mail
# Credit to https://code.tutsplus.com/tutorials/intro-to-flask-adding-a-contact-page--net-28982 for mail functionality
mail = Mail()

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'allergy.list.website@gmail.com'
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

mail.init_app(app)

# Configure SQLite3 Database
conn = sqlite3.connect('allergies.db', check_same_thread=False)
db = conn.cursor()


# Ensure responses aren't cached
@app.after_request
def after_request(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/search")
def search():
	db.execute("SELECT * FROM list ORDER BY name")
	rows = db.fetchall()
	return render_template("search.html", rests=rows)


@app.route("/ask", methods=["GET", "POST"])
def ask():
	if request.method == "GET":
		return render_template("request.html")

	else:
		rest = request.form.get("rest")

		if not request.form.get("rest_link"):
			rest_link = "NULL"

		else:
			rest_link = request.form.get("rest_link")
	
		t = (rest, rest_link)
		db.execute("INSERT INTO requests (name, link) VALUES (?, ?)", t)
		conn.commit()

		return render_template("request.html", success=True)


@app.route("/contact", methods=["GET", "POST"])
def contact():

	if request.method == "GET":
		return render_template("contact.html")

	elif request.method == "POST":
		if not os.environ.get("MAIL_PASSWORD"):
			raise RuntimeError("Mail password not set")

		subject = "Allergy Website Contact"
		msg = Message(subject, sender="allergy.list.website@gmail.com", recipients=["allergy.list.website@gmail.com"])
		msg.body = 'Sender: ' + request.form.get("address") + "\n\n" + request.form.get("message")

		mail.send(msg)

		return render_template("contact.html", success=True)


@app.route("/lookup")
def lookup():
	"""Search for restaurants similar to query"""

	if not request.args.get("q"):
		raise RuntimeError("missing query")

	q = request.args.get("q") + '%'

	t = (q,)
	db.execute("SELECT * FROM list WHERE name LIKE ? ORDER BY name", t)
	rows = db.fetchall()
	temp = []
	
	for row in rows:
		temp.append({"name": row[0], "link": row[1]})
	
	return jsonify(temp)


@app.route("/check")
def check():
	"""Check to ensure requested restaurant is not already in database and has not already been requested"""

	if not request.args.get("st"):
		raise RuntimeError("missing query")

	st = request.args.get("st")
	t = (st,)

	db.execute("SELECT * FROM list WHERE name=?", t)
	rows = db.fetchall()
	
	db.execute("SELECT * FROM requests WHERE name=?", t)
	rows2 = db.fetchall()

	rows_final = rows + rows2
	
	temp = []
	for row in rows_final:
		temp.append({"name": row[0], "link": row[1]})

	return jsonify(temp)
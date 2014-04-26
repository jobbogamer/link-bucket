import os
from datetime import datetime
from urlparse import urlparse
from flask import Flask, render_template, flash, url_for, abort, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)


def get_relative_time(seconds):
	if seconds < 60:
		return "<1m"
	elif seconds < (60 * 60):
		return str(int(seconds / 60)) + "m"
	elif seconds < (24 * 60 * 60):
		return str(int(seconds / (60 * 60))) + "h"
	elif seconds < (7 * 24 * 60 * 60):
		return str(int(seconds / (24 * 60 * 60))) + "d"
	elif seconds < (365 * 24 * 60 * 60):
		return str(int(seconds / (7 * 24 * 60 * 60))) + "w"
	else:
		return str(int(seconds / (365 * 24 * 60 * 60))) + "y"


class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(512))
	date = db.Column(db.DateTime)
	archived = db.Column(db.Boolean)
	title = db.Column(db.String)

	def __init__(self, url, date, title):
		self.url = url
		self.date = date
		self.archived = False
		self.title = title

	def __repr__(self):
		return "[Link(%d) %s]" % (self.id, self.url)


@app.route('/')
def index():
	items = Link.query.filter_by(archived = False).all()
	items = sorted(items, key=lambda link: link.id, reverse=True)
	now = datetime.now()

	ages = {}
	times = {}
	domains = {}
	for item in items:
		delta = now - item.date

		seconds = delta.total_seconds()
		times[item.id] = get_relative_time(seconds)

		days = delta.days
		if days < 1:
			ages[item.id] = "today"
		elif days < 7:
			ages[item.id] = "days"
		elif days < 28:
			ages[item.id] = "weeks"
		elif days < 365:
			ages[item.id] = "months"
		else:
			ages[item.id] = "years"

		domains[item.id] = urlparse(item.url).hostname

	return render_template('index.html', items=items, ages=ages, times=times, domains=domains)


@app.route('/add', methods=['GET', 'POST'])
def add():
	message = ''
	error = False

	if request.method == 'POST':
		item = Link(request.form['url'], datetime.now(), request.form['title'])
		db.session.add(item)
		db.session.commit()
		message = "Link added."

	if len(message) > 0:
		if error:
			flash(message, 'error')
		else:
			flash(message, 'success')

	return render_template('add.html')


if (__name__ == "__main__"):
	app.run(debug = True)

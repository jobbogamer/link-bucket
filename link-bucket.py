import os
from flask import Flask, render_template, flash, url_for, abort, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)


class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(512))
	date = db.Column(db.DateTime)
	archived = db.Column(db.Boolean)
	title = db.Column(db.String)
	icon = db.Column(db.String)

	def __init__(self, url, date, title, icon):
		self.url = url
		self.date = date
		self.archived = False
		self.title = title
		self.icon = icon

	def __repr__(self):
		return "[Link(%d) %s]" % (self.id, self.url)


@app.route('/')
def index():
	items = Link.query.filter_by(archived = False).all()
	return render_template('index.html', items=items)

if (__name__ == "__main__"):
	app.run(debug = True)

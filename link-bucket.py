import os
from flask import Flask
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
		return "<Link(" + str(self.id) + ") " + str(self.url) + " >"


@app.route('/')
def index():
	return 'Hello World!'

if (__name__ == "__main__"):
	app.run()

import os
from flask import Flask, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

import database

##### Config #####

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

try:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except KeyError as error:
	app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)

##### Routes #####

@app.route('/')
def index():
	database.create_tables()

	options = { }
	links = database.get_links()

	return render_template('index.html', options=options, links=links)

##### Main #####

if (__name__ == "__main__"):
	app.run(debug = True)
import os
from flask import Flask, url_for, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

import database
import api
from external_apis import screenshots

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

	options = {
		'time': datetime.now(),
		'title': "Linkbucket",
		'viewmode-visible': True
	}
	links = database.get_links()

	return render_template('index.html', options=options, links=links)

##### API Routes #####

@app.route('/add', methods=['GET'])
def api_add():
	url = request.args.get('url', '')
	title = request.args.get('title', '')
	return api.add(url, title)

@app.route('/check', methods=['GET'])
def api_check():
	url = request.args.get('url', '')
	return api.checl(url)

##### Template Filters #####

@app.template_filter('screenshot_url')
def screenshot_url(url):
	return screenshots.get_screenshot(url)

@app.template_filter('timesince')
def timesince(date):
	now = datetime.now()
	delta = now - date
	seconds = delta.total_seconds()

	if seconds < 60:
		return "<1m"
	elif seconds < (60 * 60):
		return str(int(seconds / 60)) + "m"
	elif seconds < (24 * 60 * 60):
		return str(int(seconds / (60 * 60))) + "h"
	else:
		return str(int(seconds / (24 * 60 * 60))) + "d"

##### Main #####

if (__name__ == "__main__"):
	app.run(debug = True)
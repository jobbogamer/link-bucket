import newrelic.agent
import os
from flask import Flask, url_for, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date

import database
import api
from external_apis import screenshots, github

##### Config #####

newrelic.agent.initialize('newrelic.ini')

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

try:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except KeyError as error:
	app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)
database.create_tables()

##### Routes #####

@app.route('/')
def index():
	database.create_tables()

	options = {
		'time': datetime.now(),
		'title': "Linkbucket",
		'viewmode_visible': True,
		'active_page': 0,
		'version': github.get_latest_release('jobbogamer', 'linkbucket')
	}
	links = database.get_links()

	return render_template('index.html', options=options, links=links)

@app.route('/archive')
def archive():
	options = {
		'time': datetime.now(),
		'title': "Archive - Linkbucket",
		'viewmode_visible': False,
		'active_page': 1,
		'version': github.get_latest_release('jobbogamer', 'linkbucket')
	}
	links = database.get_archived_links()

	return render_template('archive.html', options=options, links=links)

@app.route('/stats')
def stats():
	options = {
		'time': datetime.now(),
		'title': "Stats - Linkbucket",
		'viewmode_visible': False,
		'active_page': 2,
		'version': github.get_latest_release('jobbogamer', 'linkbucket')
	}
	stats = database.get_stats()
	if stats is None:
		database.create_stats()
		stats = database.get_stats()

	stats.move_history_if_necessary()

	histories = {
		'add': stats.get_add_history(),
		'click': stats.get_click_history()
	}

	return render_template('stats.html', options=options, stats=stats, histories=histories)

##### API Routes #####

@app.route('/api/add', methods=['GET'])
def api_add():
	url = request.args.get('url', '')
	title = request.args.get('title', '')
	return api.add(url, title)

@app.route('/api/archive', methods=['GET'])
def api_archive():
	id = int(request.args.get('id', 0))
	return api.archive(id)

@app.route('/api/click', methods=['GET'])
def api_click():
	id = int(request.args.get('id', 0))
	return api.click(id)

@app.route('/api/delete', methods=['GET'])
def api_delete():
	id = int(request.args.get('id', 0))
	return api.delete(id)

@app.route('/api/facebook/lastchecked', methods=['GET'])
def api_facebook_lastchecked():
	thread_id = request.args.get('id', '')
	return api.facebook_last_message_id(thread_id)

@app.route('/api/star', methods=['GET'])
def api_star():
	id = int(request.args.get('id', 0))
	return api.star(id)

@app.route('/api/title', methods=['GET'])
def api_title():
	id = int(request.args.get('id', 0))
	new_title = request.args.get('title', '')
	return api.title(id, new_title)

@app.route('/api/unarchive', methods=['GET'])
def api_unarchive():
	id = int(request.args.get('id', 0))
	return api.unarchive(id)

@app.route('/api/unstar', methods=['GET'])
def api_unstar():
	id = int(request.args.get('id', 0))
	return api.unstar(id)

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

@app.template_filter('timesince_long')
def timesince_long(the_date):
	now = datetime.now()
	delta = now - the_date
	seconds = delta.total_seconds()

	if seconds < 60:
		return "less than a minute ago"
	elif seconds < (60 * 60):
		return str(int(seconds / 60)) + " minutes ago"
	elif seconds < (24 * 60 * 60):
		return str(int(seconds / (60 * 60))) + " hours ago"
	else:
		today = date.today()
		date_short = the_date.date()
		delta = today - date_short
		days = delta.days
		if days == 1:
			return "yesterday"
		else:
			return str(days) + " days ago"

@app.template_filter('thousands_separators')
def thousands_separators(num):
	return "{:,}".format(num)

##### Main #####

if (__name__ == "__main__"):
	app.run(debug = True)
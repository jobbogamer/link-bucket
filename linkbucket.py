import newrelic.agent
import os
from flask import Flask, url_for, render_template, request, jsonify
from datetime import datetime, date

from utils import utils
from model import database
from routes import api
from external_apis import screenshots, github

##### Config #####

newrelic.agent.initialize('newrelic.ini')

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

try:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except KeyError as error:
	app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

database.db.init_app(app)

##### Routes #####

@app.route('/')
def index():
	database.create_tables()

	options = {
		'time': datetime.now(),
		'title': "Inbox - Linkbucket",
		'viewmode_visible': False,
		'active_page': 0,
	}
	links = database.get_links()

	stats = database.get_stats()
	stats.move_history_if_necessary()
	stats.increment_views()

	return render_template('index.html', options=options, links=links)

@app.route('/archive')
def archive():
	options = {
		'time': datetime.now(),
		'title': "Archive - Linkbucket",
		'viewmode_visible': False,
		'active_page': 1,
	}
	links = database.get_archived_links()

	stats = database.get_stats()
	stats.move_history_if_necessary()
	stats.increment_views()

	return render_template('archive.html', options=options, links=links)

@app.route('/search', methods=['GET'])
def search():
	query = request.args.get('q', '')
	options = {
		'time': datetime.now(),
		'title': 'Search results for "{0}" - Linkbucket'.format(query),
		'viewmode_visible': False,
		'active_page': -1,
		'query': query
	}
	links = database.search_for_links(query)

	stats = database.get_stats()
	stats.move_history_if_necessary()
	stats.increment_views()

	return render_template('search.html', options=options, links=links)

@app.route('/stats')
def stats():
	options = {
		'time': datetime.now(),
		'title': "Stats - Linkbucket",
		'viewmode_visible': False,
		'active_page': 2,
		'releases': github.get_latest_releases('jobbogamer', 'linkbucket', 3)
	}
	
	stats = database.get_stats()
	stats.move_history_if_necessary()
	stats.increment_views()

	histories = {
		'add': stats.get_add_history(),
		'click': stats.get_click_history(),
		'view': stats.get_view_history()
	}

	return render_template('stats.html', options=options, stats=stats, histories=histories)

##### API Routes #####

@app.route('/api/add', methods=['GET'])
def api_add():
	url = request.args.get('url', '')
	title = request.args.get('title', '')
	return api.add(url, title)

@app.route('/api/all', methods=['GET'])
def api_all():
	return api.all()

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

@app.route('/api/facebook/parse', methods=['POST'])
def api_facebook_parse():
	thread_id = request.form['thread_id']
	most_recent_id = request.form['most_recent_id']
	json = request.form['json']
	return api.facebook_parse_messages(thread_id, most_recent_id, json)

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
	return utils.timesince(date)

@app.template_filter('timesince_long')
def timesince_long(the_date):
	now = datetime.now()
	delta = now - the_date
	seconds = delta.total_seconds()

	if seconds < 60:
		return "less than a minute ago"
	elif seconds < (60 * 60):
		i = int(seconds / 60)
		s = "" if i == 1 else "s"
		return str(i) + " minute{0} ago".format(s)
	elif seconds < (24 * 60 * 60):
		i = int(seconds / (60 * 60))
		s = "" if i == 1 else "s"
		return str(i) + " hour{0} ago".format(s)
	else:
		i = int(seconds / (24 * 60 * 60))
		if i == 1:
			return "yesterday"
		else:
			return str(i) + " days ago"

@app.template_filter('thousands_separators')
def thousands_separators(num):
	return "{:,}".format(num)

##### Main #####

if (__name__ == "__main__"):
	app.run(debug=True)

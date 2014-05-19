# -*- coding: utf-8 -*-

import os
import facebook
import re
import HTMLParser
from urllib2 import urlopen, Request
from datetime import datetime, timedelta
from urlparse import urlparse
from flask import Flask, render_template, flash, url_for, request, redirect, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

try:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
except KeyError as error:
	app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)

base_url = 'http://linkbucket.josh-asch.net'

###############################################################################
# Database model objects                                                      #
###############################################################################

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

		if (len(title) > 0) and (title != 'Title'):
			self.title = title
		else:
			autotitle = get_title(url)
			if autotitle != '!!!null!!!':
				self.title = autotitle
			else:
				self.title = '(No title)'

	def __repr__(self):
		return "[Link(%d) %s]" % (self.id, self.url)


class FB(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	app_id = db.Column(db.String(50))
	app_secret = db.Column(db.String(50))
	code = db.Column(db.String(512))
	access_token = db.Column(db.String(512))
	expiry = db.Column(db.DateTime)

	def __init__(self, app_id, app_secret):
		self.app_id = app_id
		self.app_secret = app_secret
		self.code = ''
		self.access_token = ''

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	last_checked = db.Column(db.String(64))

	def __init__(self, last_checked):
		self.last_checked = last_checked

class Stats(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	links_created = db.Column(db.Integer)
	links_clicked = db.Column(db.Integer)
	links_archived = db.Column(db.Integer)
	links_unarchived = db.Column(db.Integer)
	links_edited = db.Column(db.Integer)
	searches_performed = db.Column(db.Integer)
	one_result = db.Column(db.Boolean)
	no_results = db.Column(db.Boolean)
	oldest_link = db.Column(db.Integer)

	def __init__(self):
		self.links_created = 0
		self.links_clicked = 0
		self.links_archived = 0
		self.links_unarchived = 0
		self.links_edited = 0
		self.searches_performed = 0
		self.one_result = False
		self.no_results = False
		self.oldest_link = 0


###############################################################################
# Interaction methods                                                         #
###############################################################################

def get_item_by_id(id):
	item = Link.query.filter_by(id=id).first()
	return item

def get_item_list():
	items = Link.query.filter_by(archived = False).all()
	items = sorted(items, key=lambda link: link.date, reverse=True)
	return items

def get_archive_list():
	items = Link.query.filter_by(archived = True).all()
	items = sorted(items, key=lambda link: link.date, reverse=True)
	return items

def add_item(url, date, title):
	new_item = Link(url, date, title)
	db.session.add(new_item)
	db.session.commit()

def archive_item(id):
	item = get_item_by_id(id)
	item.archived = True
	item.date = datetime.now()
	db.session.commit()

def unarchive_item(id):
	item = get_item_by_id(id)
	item.archived = False
	item.date = datetime.now()
	db.session.commit()

def edit_item_title(id, new_title):
	item = get_item_by_id(id)
	item.title = new_title
	db.session.commit()

def delete_item(id):
	item = get_item_by_id(id)
	db.session.delete(item)
	db.session.commit()

def is_valid_url(url):
	return urlparse(request.form['url']).hostname is not None

def get_domain(url):
	return urlparse(url).hostname.replace('www.', '')

def get_title(url):
	try:
		page = urlopen(url.encode('utf-8'), timeout=10).read()
		lowercase_page = page.lower()
		tagstart = lowercase_page.find('<title') + 6
		start = lowercase_page.find('>', tagstart) + 1
		end = lowercase_page.find('</title>')
		parser = HTMLParser.HTMLParser()
		if (tagstart == -1) or (start == -1) or (end == -1):
			return '(No title)'
		else:
			return parser.unescape(page[start:end])
	except Exception as error:
		return '!!!null!!!'

def get_relative_time(date):
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

def get_opacity_from_age(date):
	now = datetime.now()
	delta = now - date
	days = delta.days

	if days < 1:
		return "100"
	elif days < 3:
		return "90"
	elif days < 5:
		return "80"
	elif days < 7:
		return "70"
	elif days < 14:
		return "60"
	elif days < 21:
		return "50"
	elif days < 28:
		return "40"
	else:
		return "30"

def delete_if_too_old(item):
	now = datetime.now()
	delta = now - item.date
	days = delta.days

	if days >= 7:
		delete_item(item.id)

def get_youtube_embed_url(url):
	if "youtube.com/watch?v" in url:
		if '&' in url:
			next_param_pos = url.find("&")
			return url[:next_param_pos].replace("watch?v=", "embed/")
		else:
			return url.replace("watch?v=", "embed/")
	elif "youtu.be" in url:
		return url.replace("youtu.be", "youtube.com/embed")
	elif "yourepeat.com/watch?v" in url:
		return url.replace("repeat.com/watch?v=", "tube.com/embed/")

	return None

def perform_search(searchterm, archive=False):
	if archive:
		items = get_archive_list()
	else:
		items = get_item_list()

	matched = []
	not_matched = []
	searchterm = searchterm.lower()

	for item in items:
		if (searchterm in item.title.lower()) or (searchterm in item.url.lower()):
			matched.append(item.id)
		else:
			not_matched.append(item.id)

	return jsonify(matched=matched, not_matched=not_matched)

def get_travis_info():
	url = 'https://api.travis-ci.org/repos/jobbogamer/link-bucket'
	headers = {'User-Agent': 'LinkBucket/1.0.0', 'Accept': 'application/vnd.travis-ci.2+json'}
	request = Request(url, headers=headers)
	results = urlopen(request).read().replace('null', 'None').replace('false', 'False').replace('true', 'True')
	repo_data = eval(results)['repo']

	build_id = repo_data['last_build_id']
	build_no = int(repo_data['last_build_number']) + 87

	url = 'https://api.travis-ci.org/repos/jobbogamer/link-bucket/builds/' + str(build_id)
	headers = {'User-Agent': 'LinkBucket/1.0.0', 'Accept': 'application/vnd.travis-ci.2+json'}
	request = Request(url, headers=headers)
	results = urlopen(request).read().replace('null', 'None').replace('false', 'False').replace('true', 'True')
	commit_data = eval(results)['commit']

	sha1 = commit_data['sha'][:10]
	date = commit_data['committed_at']
	message = commit_data['message']
	url = commit_data['compare_url']

	date = get_relative_time(datetime.strptime(date[0:19], '%Y-%m-%dT%H:%M:%S'))
	if date.endswith('m'):
		if '<' in date:
			date = "Less than a minute ago"
		elif '1' in date:
			date = "A minute ago"
		else:
			date = date.replace('m', ' minutes ago')
	elif date.endswith('h'):
		if '1' in date:
			date = 'An hour ago'
		else:
			date = date.replace('h', ' hours ago')
	else:
		if '1' in date:
			date = 'Yesterday'
		else:
			date = date.replace('d', ' days ago')

	data = {'build_no': build_no, 'date': date, 'message': message, 'url': url}

	return data

def get_stats():
	stats = Stats.query.filter_by(id = 1).first()
	return stats

def increment_links_created():
	stats = get_stats()
	stats.links_created = stats.links_created + 1
	db.session.commit()
	return stats.links_created

def increment_links_clicked():
	stats = get_stats()
	stats.links_clicked = stats.links_clicked + 1
	db.session.commit()
	return stats.links_clicked

def increment_links_archived():
	stats = get_stats()
	stats.links_archived = stats.links_archived + 1
	db.session.commit()
	return stats.links_archived

def increment_links_unarchived():
	stats = get_stats()
	stats.links_unarchived = stats.links_unarchived + 1
	db.session.commit()
	return stats.links_unarchived

def increment_links_edited():
	stats = get_stats()
	stats.links_edited = stats.links_edited + 1
	db.session.commit()
	return stats.links_edited

def increment_searches_performed():
	stats = get_stats()
	stats.searches_performed = stats.searches_performed + 1
	db.session.commit()
	return stats.searches_performed

def set_oldest_link(age):
	stats = get_stats()
	if age > stats.oldest_link:
		stats.oldest_link = age
		db.session.commit()
	return stats.oldest_link


###############################################################################
# Routing methods                                                             #
###############################################################################

@app.route('/')
def index():
	db.create_all()

	items = get_item_list()
	now = datetime.now()

	opacities = {}
	times = {}
	domains = {}
	positions = {}
	youtubes = {}

	position = len(items);

	for item in items:
		times[item.id] = get_relative_time(item.date)
		opacities[item.id] = get_opacity_from_age(item.date)
		domains[item.id] = get_domain(item.url)

		youtube = get_youtube_embed_url(item.url)
		if youtube is not None:
			youtubes[item.id] = youtube

		positions[item.id] = position
		position -= 1

	return render_template('index.html', title='Link Bucket', emptymessage='No links yet.', items=items, opacities=opacities, times=times, domains=domains, positions=positions, youtubes=youtubes)


@app.route('/add', methods=['GET', 'POST'])
def add():
	message = ''
	error = False

	previous_title = ''
	previous_url = ''

	if request.method == 'POST':
		url = request.form['url']
		title = request.form['title']
		date = datetime.now()

		if not is_valid_url(url):
			message = 'An invalid URL was given.'
			error = True
			previous_title = title
			previous_url = url

		else:
			add_item(url, date, title)
			if title == 'Title':
				message = "Link added: " + get_domain(url)
			else:
				message = "Link added: " + title + " (" + get_domain(url) + ")"

	if len(message) > 0:
		if error:
			flash(message, 'error')
		else:
			flash(message, 'success')

	return render_template('add.html', title='Link Bucket - Add Link', previous_title=previous_title, previous_url=previous_url)


@app.route('/archive')
def view_archive():
	items = get_archive_list()
	items = sorted(items, key=lambda link: link.date, reverse=True)
	now = datetime.now()

	opacities = {}
	times = {}
	domains = {}
	positions = {}
	data_edited = False
	position = len(items)

	for item in items:
		delete_if_too_old(item)

		times[item.id] = get_relative_time(item.date)
		opacities[item.id] = 100
		domains[item.id] = get_domain(item.url)

		positions[item.id] = position
		position -= 1

	return render_template('archive.html', title='Link Bucket - Archive', emptymessage='The archive is empty.', items=items, opacities=opacities, times=times, domains=domains, positions=positions)

@app.route('/stats')
def stats():
	travis = get_travis_info()
	return render_template('stats.html', title='Link Bucket - Stats', travis=travis)

###############################################################################
# API methods                                                                 #
###############################################################################

@app.route('/archive/<int:id>')
def archive(id):
	archive_item(id)
	return redirect(url_for('index') + "#" + str(request.args.get('scrollto', '')))

@app.route('/unarchive/<int:id>')
def unarchive(id):
	unarchive_item(id)
	return redirect(url_for('view_archive') + "#" + str(request.args.get('scrollto', '')))

@app.route('/edit/<int:id>')
def edit(id):
	title = request.args.get('title', '(No title)')
	edit_item_title(id, title)
	return redirect(url_for('index') + "#" + str(request.args.get('scrollto', '')))

@app.route('/title/<path:url>')
def title(url):
	args = request.args
	full_url = url
	if len(args) > 0:
		full_url += "?"
		for key in args:
			full_url += key + "=" + args[key] + "&"
		full_url = full_url[:-1]

	return get_title(full_url)

@app.route('/search/<path:searchterm>')
def search(searchterm):
	return perform_search(searchterm)

@app.route('/searcharchive/<path:searchterm>')
def search_archive(searchterm):
	return perform_search(searchterm, True)

###############################################################################
# Facebook routing methods                                                    #
###############################################################################

@app.route('/fb')
def fb():
	details = FB.query.filter_by(id = 1).first()
	if details is None:
		details = FB('776255502385741', '3fc41ad7c7cbd4084c341d068c5e02f3')
		db.session.add(details)
		db.session.commit()
	return redirect(facebook_login_url())

@app.route('/fb_logged_in')
def handle_fb():
	if 'code' in request.args:
		details = FB.query.filter_by(id = 1).first()
		details.code = request.args['code']
		db.session.commit()
		return redirect(facebook.get_access_token_from_code(details.code, base_url + url_for('handle_fb'), details.app_id, details.app_secret))

	return '''  <script type="text/javascript">
				var token = window.location.href.split("access_token=")[1];
				window.location = "/fb_token/" + token;
			</script> '''

@app.route('/fb_token/<token>')
def fb_token(token):
	pos = token.find('&expires_in=')
	expires_in = int(token[(pos + 12):])
	delta = timedelta(seconds=expires_in)
	expiry = datetime.now() + delta

	details = FB.query.filter_by(id = 1).first()
	details.access_token = token[:pos]
	details.expiry = expiry
	db.session.commit()

	get_facebook_message_links()

	return redirect(url_for('index'))

###############################################################################
# Facebook methods                                                            #
###############################################################################

def facebook_login_url():
	details = FB.query.filter_by(id = 1).first()
	url = facebook.auth_url(details.app_id, base_url + url_for('handle_fb'), perms=['read_mailbox'])
	url += "&response_type=token"
	return url

def get_facebook_message_links():
	messages = []

	details = FB.query.filter_by(id = 1).first()
	api = facebook.GraphAPI(access_token = details.access_token)
	conversation = api.get_object('486492038125631')

	last_message_time = conversation['updated_time']
	previous_messages_url = conversation['comments']['paging']['next']

	fetched_messages = conversation['comments']['data']
	last_checked = get_last_checked_id()
	found_last_checked = False

	for message in fetched_messages:
		if message['id'] > last_checked:
			messages.append(message)

		if message['id'] == last_checked:
			found_last_checked = True

	if not found_last_checked:
		messages = find_last_checked(last_checked, previous_messages_url, messages)

	if len(messages) > 0:
		biggest_id = '0'
		most_recent_message = None
		for message in messages:
			if message['id'] > biggest_id:
				biggest_id = message['id']
				most_recent_message = message

		set_last_checked_id(biggest_id)

	links = []
	message_fail_count = 0
	link_fail_count = 0

	for message in messages:
		try:
			text = message['message'].replace('\\', '')
			if "http" in text:
				date = datetime.strptime(message['created_time'][0:19], '%Y-%m-%dT%H:%M:%S')
				delta = datetime.now() - datetime.utcnow()
				date = date + delta
				message_link = re.search("(?P<url>https?://[^\s]+)", text).group("url")
				link_dict = {'url': message_link, 'title': text.replace(message_link, '').strip(), 'date': date}
				if ':at:' in link_dict['title']:
					link_dict['title'] = ''
				links.append(link_dict)
		except KeyError as error:
			pass
		except Exception as error:
			print "An exception occurred: " + str(type(error)) + " - " + str(error)
			print "The offending message was: \"" + str(text) + "\""
			message_fail_count += 1

	for link in links:
		try:
			add_item(link['url'], link['date'], link['title'])
		except Exception as error:
			print "An exception occurred: " + str(type(error)) + " - " + str(error)
			print "The offending link was: \"" + str(link['url']) + "\" with title \"" + str(link['title']) + "\""
			link_fail_count += 1

	if message_fail_count > 0:
		unit = " message" if message_fail_count == 1 else " messages"
		flash(str(message_fail_count) + unit + " failed to parse.", 'error')

	if link_fail_count > 0:
		unit - " link" if link_fail_count == 1 else " links"
		flash(str(link_fail_count) + unit + " failed to parse.", 'error')

def find_last_checked(last_checked, previous_messages_url, messages):
	found_last_checked = False

	while not found_last_checked:
		data = eval(urlopen(previous_messages_url).read())
		fetched_messages = data['data']

		for message in fetched_messages:
			if message['id'] >= last_checked:
				messages.append(message)

			if message['id'] == last_checked:
				found_last_checked = True

		previous_messages_url = data['paging']['next'].replace('\\', '')

	return messages

def get_last_checked_id():
	details = Message.query.filter_by(id = 1).first()

	if details is None:
		set_last_checked_id('486492038125631_1398714530646')
		return '486492038125631_1398714530646'

	return details.last_checked

def set_last_checked_id(id):
	details = Message.query.filter_by(id = 1).first()

	if details is None:
		details = Message(id)
		db.session.add(details)
	else:
		details.last_checked = id

	db.session.commit()

if (__name__ == "__main__"):
	app.run(debug = True)
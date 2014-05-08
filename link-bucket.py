# -*- coding: utf-8 -*-

import os
import facebook
import re
from urllib2 import urlopen
from pprint import pformat
from datetime import datetime, timedelta
from urlparse import urlparse
from flask import Flask, render_template, flash, url_for, abort, request, jsonify, redirect
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "d47d2b74ff64e5a6ae5aedd4edebeaf1"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost:5432"

db = SQLAlchemy(app)

base_url = 'http://linkbucket.josh-asch.net'

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

	for message in messages:
		try:
			text = message['message']
			if "http" in text:
				date = datetime.strptime(message['created_time'][0:19], '%Y-%m-%dT%H:%M:%S')
				delta = datetime.now() - datetime.utcnow()
				date = date + delta
				message_link = re.search("(?P<url>https?://[^\s]+)", text).group("url")
				link_dict = {'url': message_link, 'title': text.replace(message_link, '').strip(), 'date': date}
				links.append(link_dict)
		except KeyError as error:
			pass

	for link in links:
		new_link = Link(link['url'], link['date'], link['title'])
		db.session.add(new_link)

	db.session.commit()

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

@app.route('/')
def index():
	db.create_all()

	items = Link.query.filter_by(archived = False).all()
	items = sorted(items, key=lambda link: link.id, reverse=True)
	now = datetime.now()

	opacities = {}
	times = {}
	domains = {}
	for item in items:
		delta = now - item.date

		seconds = delta.total_seconds()
		times[item.id] = get_relative_time(seconds)

		days = delta.days
		if days < 1:
			opacities[item.id] = "100"
		elif days < 3:
			opacities[item.id] = "90"
		elif days < 5:
			opacities[item.id] = "80"
		elif days < 7:
			opacities[item.id] = "70"
		elif days < 14:
			opacities[item.id] = "60"
		elif days < 21:
			opacities[item.id] = "50"
		elif days < 28:
			opacities[item.id] = "40"
		else:
			opacities[item.id] = "30"

		domains[item.id] = urlparse(item.url).hostname.replace('www.', '')

	return render_template('index.html', title='Link Bucket', emptymessage='No links yet.', items=items, opacities=opacities, times=times, domains=domains)


@app.route('/add', methods=['GET', 'POST'])
def add():
	message = ''
	error = False

	if request.method == 'POST':
		item = Link(request.form['url'], datetime.now(), request.form['title'])
		db.session.add(item)
		db.session.commit()
		message = "Link added. (" + str(urlparse(request.form['url']).hostname.replace('www.', '')) + ")"

	if len(message) > 0:
		if error:
			flash(message, 'error')
		else:
			flash(message, 'success')

	return render_template('add.html', title='Link Bucket - Add Link')


@app.route('/archive')
def view_archive():
	items = Link.query.filter_by(archived = True).all()
	items = sorted(items, key=lambda link: link.date, reverse=True)
	now = datetime.now()

	opacities = {}
	times = {}
	domains = {}
	data_edited = False;
	for item in items:
		delta = now - item.date

		days = delta.days
		if days > 7:
			db.session.delete(item)
			data_edited = True

		seconds = delta.total_seconds()
		times[item.id] = get_relative_time(seconds)
		opacities[item.id] = 100
		domains[item.id] = urlparse(item.url).hostname.replace('www.', '')

	if data_edited:
		db.session.commit()

	return render_template('index.html', title='Link Bucket - Archive', emptymessage='The archive is empty.', items=items, opacities=opacities, times=times, domains=domains)


@app.route('/archive/<int:id>')
def archive(id):
	item = Link.query.filter_by(id=id).first()
	item.archived = True
	item.date = datetime.now()
	db.session.commit()
	return redirect(url_for('index'))


@app.route('/api/create/')
def api_create_no_params():
	return jsonify(success=False, error_code=2, error_msg="Incorrect number of parameters")

@app.route('/api/create/<anything>/')
def api_create_one_param(anything):
	return jsonify(success=False, error_code=2, error_msg="Incorrect number of parameters")

@app.route('/api/create/<title>/<path:url>')
def api_create(title, url):
	if not url.startswith("http://") and '.' in url:
		url = "http://" + url

	if len(urlparse(url).netloc) == 0:
		return jsonify(success=False, error_code=1, error_msg="Invalid URL")
	else:
		item = Link(url, datetime.now(), title)
		db.session.add(item)
		db.session.commit()
		return jsonify(success=True, error_code=0, error_msg="")


@app.route('/api/archive/')
def api_archive_no_params():
	return jsonify(success=False, error_code=2, error_msg="Incorrect number of parameters")

@app.route('/api/archive/<int:id>/')
def api_archive(id):
	item = Link.query.filter_by(id=id).first()
	item.archived = True
	item.date = datetime.now()
	db.session.commit()
	return jsonify(success=True, error_code=0, error_msg="")



@app.route('/api/destroy/')
def api_destroy_no_params():
	return jsonify(success=False, error_code=2, error_msg="Incorrect number of parameters")

@app.route('/api/destroy/<int:id>/')
def api_destroy(id):
	item = Link.query.filter_by(id=id).first()
	db.session.delete(item)
	db.session.commit()
	return jsonify(success=True, error_code=0, error_msg="")


@app.route('/fb')
def fb():
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


if (__name__ == "__main__"):
	app.run(debug = True)

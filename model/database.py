from utils import utils
import pickle
from external_apis import readability
from datetime import datetime, date
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##### Model classes #####

class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	url = db.Column(db.String)
	title = db.Column(db.String)
	date = db.Column(db.DateTime)

	archived = db.Column(db.Boolean)
	unread = db.Column(db.Boolean)
	starred = db.Column(db.Boolean)

	domain = db.Column(db.String)
	excerpt = db.Column(db.String)
	word_count = db.Column(db.Integer)
	image_url = db.Column(db.String)
	embed_url = db.Column(db.String)
	embed_type = db.Column(db.Integer)

	def __init__(self, url, date):
		self.url = url
		self.date = date
		self.archived = False
		self.unread = True
		self.starred = False

		parsed = readability.parse(url)
		if parsed is None:
			self.title = "(No title)"
			self.domain = utils.find_domain(url)
		else:
			self.title = parsed.title
			self.domain = parsed.domain
			self.excerpt = parsed.excerpt
			self.word_count = parsed.word_count
			self.image_url = parsed.image_url

		self.embed_url, self.embed_type = _find_embed(url)


class Stats(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	last_day = db.Column(db.DateTime)

	total_added = db.Column(db.Integer)
	total_archived = db.Column(db.Integer)
	total_clicked = db.Column(db.Integer)
	total_deleted = db.Column(db.Integer)
	total_edited = db.Column(db.Integer)
	total_searches = db.Column(db.Integer)
	total_unarchived = db.Column(db.Integer)

	add_history = db.Column(db.PickleType)
	click_history = db.Column(db.PickleType)

	def __init__(self):
		self.last_day = date.today()

		self.total_added = 0
		self.total_archived = 0
		self.total_clicked = 0
		self.total_deleted = 0
		self.total_edited = 0
		self.total_searches = 0
		self.total_unarchived = 0

		add_history_list = [0]*28
		self.add_history = pickle.dumps(add_history_list, -1)

		click_history_list = [0]*28
		self.click_history = pickle.dumps(click_history_list, -1)

	def __repr__(self):
		return "[Stats - add({0}), arc({1}), cli({2}), del({3}), edi({4}), sea({5}), una({6})]".format(
			self.total_added, self.total_archived, self.total_clicked,
			self.total_deleted, self.total_edited, self.total_searches,
			self.total_unarchived)

	def get_add_history(self):
		return pickle.loads(self.add_history)

	def get_click_history(self):
		return pickle.loads(self.click_history)

	def increment_adds(self):
		self.move_history_if_necessary()
		add_history_list = self.get_add_history()
		add_history_list[27] += 1
		self.set_add_history(add_history_list)
		self.total_added += 1
		commit_changes()

	def increment_archives(self):
		self.total_archived += 1
		commit_changes()

	def increment_clicks(self):
		self.move_history_if_necessary()
		click_history_list = self.get_click_history()
		click_history_list[27] += 1
		self.set_click_history(click_history_list)
		self.total_clicked += 1
		commit_changes()

	def increment_deletes(self):
		self.total_deleted += 1
		commit_changes()

	def increment_edits(self):
		self.total_edited += 1
		commit_changes()

	def increment_searches(self):
		self.total_searches += 1
		commit_changes()

	def increment_unarchives(self):
		self.total_unarchived += 1
		commit_changes()

	def move_history(self, days):
		add_history_list = self.get_add_history()
		click_history_list = self.get_click_history()

		add_history_list = add_history_list[days:] + [0]*days
		click_history_list = click_history_list[days:] + [0]*days

		self.set_add_history(add_history_list)
		self.set_click_history(click_history_list)

	def move_history_if_necessary(self):
		today = date.today()
		delta = today - self.last_day.date()
		days = delta.days

		if days > 0:
			self.move_history(days)
			self.last_day = today
			commit_changes()

	def set_add_history(self, add_history_list):
		self.add_history = pickle.dumps(add_history_list, -1)
		commit_changes()

	def set_click_history(self, click_history_list):
		self.click_history = pickle.dumps(click_history_list, -1)
		commit_changes()


class FacebookConversation(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	thread_id = db.Column(db.String)
	last_message_id = db.Column(db.String)

	def __init__(self, thread_id, last_message_id):
		self.thread_id= thread_id
		self.last_message_id = last_message_id

	def set_last_message_id(self, id):
		self.last_message_id = id
		commit_changes()


##### Private API #####

def _find_embed(url):
	url_l = url.lower()

	if 'youtube.com/watch?v' in url_l:
		if '&' in url_l:
			param_pos = url_l.find('&')
			return (url[:param_pos].replace('watch?v=', 'embed/'), 1)
		else:
			return (url.replace('watch?v=', 'embed/'), 1)

	elif 'youtu.be' in url_l:
		return (url.replace('.be', 'be.com/embed'), 1)

	elif 'yourepeat.com/watch?v' in url_l:
		return (url.replace('repeat', tube).replace('watch?v=', '/embed'), 1)

	elif url_l.endswith('.jpg') or url_l.endswith('.jpeg') or url_l.endswith('.png') or url_l.endswith('.gif'):
		if not ('dropbox.com' in url_l):
			return (url, 2)

	return ('', 0)

##### Public API #####

def add_facebook_conversation(thread_id, last_message_id):
	conversation = FacebookConversation(thread_id, last_message_id)
	db.session.add(conversation)
	commit_changes()

def add_link(url, date):
	new_link = Link(url, date)
	db.session.add(new_link)
	db.session.commit()
	get_stats().increment_adds()
	return new_link

def archive_link(id):
	link = get_link_by_id(id)
	link.archived = True
	link.date = datetime.now()
	db.session.commit()
	get_stats().increment_archives()

def create_stats():
	stats = Stats()
	db.session.add(stats)
	db.session.commit()

def create_tables():
	db.create_all()

def commit_changes():
	db.session.commit()

def delete_link(id):
	link = get_link_by_id(id)
	db.session.delete(link)
	db.session.commit()
	get_stats().increment_deleted()

def edit_title(id, new_title):
	link = get_link_by_id(id)
	link.title = new_title
	db.session.commit()
	get_stats().increment_edits()
	return link

def edit_title_without_counting(id, new_title):
	link = get_link_by_id(id)
	link.title = new_title
	db.session.commit()
	return link

def get_facebook_conversation(thread_id):
	conversation = FacebookConversation.query.filter_by(thread_id = thread_id).first()
	return conversation

def get_archived_links():
	links = Link.query.filter_by(archived = True).all()
	links = sorted(links, key=lambda link: link.date, reverse=True)
	return links

def get_link_by_id(id):
	link = Link.query.filter_by(id = id).first()
	return link

def get_links():
	links = Link.query.filter_by(archived = False).all()
	links = sorted(links, key=lambda link: link.date, reverse=True)
	return links

def get_stats():
	stats = Stats.query.filter_by(id = 1).first()
	return stats

def mark_link_as_read(id):
	link = get_link_by_id(id)
	link.unread = False
	db.session.commit()
	get_stats().increment_clicks()

def mark_link_as_starred(id):
	link = get_link_by_id(id)
	if not (link.unread):
		link.starred = True
		db.session.commit()
		return True
	return False

def mark_link_as_unread(id):
	link = get_link_by_id(id)
	link.unread = True
	db.session.commit()

def mark_link_as_unstarred(id):
	link = get_link_by_id(id)
	link.starred = False
	db.session.commit()

def unarchive_link(id):
	link = get_link_by_id(id)
	link.archived = False
	link.date = datetime.now()
	db.session.commit()
	get_stats().increment_unarchives()

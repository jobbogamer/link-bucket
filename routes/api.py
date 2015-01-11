from datetime import datetime, timedelta
from flask import jsonify
from utils import utils
from external_apis import screenshots
from model import database
import json

def add(url, title=''):
	result = { }

	if len(url) > 0:
		if utils.page_exists(url):
			try:
				link = database.add_link(url, datetime.now())
				if title and (len(title) > 0):
					database.edit_title_without_counting(link.id, title)

				if link.embed_type == 0:
					duration = utils.reading_time(link.word_count)
				elif link.embed_type == 1:
					duraton = utils.video_duration(link.word_count)

				result = {
					'success': True,
					'valid_url': True,
					'link': {
						'id': link.id,
						'title': link.title,
						'url': link.url,
						'domain': link.domain,
						'embed_type': link.embed_type,
						'embed_url': link.embed_url,
						'image_url': link.image_url,
						'screenshot_url': screenshots.get_screenshot(link.url),
						'duration': duration
					}
				}
	
			except Exception as error:
				print "(API) Couldn't add link. " + str(type(error)) + " - " + str(error)
				result = { 'success': False, 'valid_url': True, 'message': str(error) }

		else:
			result = { 'success': False, 'valid_url': False, 'no_url': False }

	else:
		result = { 'success': False, 'valid_url': False, 'no_url': True}

	return jsonify(result)


def all():
	try:
		links = database.get_all_links()
		json_links = []
		for link in links:
			json_link = {
				'id': link.id,
				'title': link.title,
				'url': link.url,
				'domain': link.domain,
				'embed_type': link.embed_type,
				'embed_url': link.embed_url,
				'image_url': link.image_url,
				'screenshot_url': screenshots.get_screenshot(link.url),
				'date': utils.timesince(link.date)
			}
			json_links.append(json_link)

		result = {
			'success': True,
			'links': json_links
		}

	except Exception as error:
		result = {
			'success': False,
			'message': str(error)
		}

	return jsonify(result)


def archive(id):
	result = { }

	try:
		database.archive_link(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def click(id):
	result = { }

	try:
		link = database.get_link_by_id(id)
		if link.unread and not link.starred:
			result['moved_to_archive'] = True
			database.archive_link(id)
		else:
			result['moved_to_archive'] = False

		database.mark_link_as_read(id)
		result['success'] = True

	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def delete(id):
	result = { }

	try:
		database.delete_link(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def facebook_last_message_id(thread_id):
	result = { }

	try:
		conversation = database.get_facebook_conversation(thread_id)
		if not(conversation is None):
			result = {
				'success': True,
				'thread_id': thread_id,
				'last_message_id': conversation.last_message_id
			}
		else:
			result = {
				'success': True,
				'thread_id': thread_id,
				'last_message_id': None
			}
	except Exception as error:
		result = {
			'success': False,
			'message': str(error)
		}

	return jsonify(result)


def facebook_parse_messages(thread_id, last_message_id, json_string):
	result = { }

	try:
		conversation = database.get_facebook_conversation(thread_id)
		if not(conversation is None):
			conversation.set_last_message_id(last_message_id)
		else:
			database.add_facebook_conversation(thread_id, last_message_id)

		messages = json.loads(json_string)

		links = []
		for message in messages:
			if 'text' in message:
				if not(':ig:' in message['text']):
					urls = utils.extract_links(message['text'])
					date = utils.parse_date(message['date'])
					title = ''

					if ':rt:' in message['text']:
						title = utils.extract_title(message['text'], urls)
					
					for i in range(len(urls)):
						if 'linkbucket.joshasch.com' not in urls[i]:
							link = database.add_link(urls[i], date)
							if len(title) > 0:
								if len(urls) > 1:
									link = database.edit_title_without_counting(link.id, title + " (" + str(i+1) + ")")
								else:
									link = database.edit_title_without_counting(link.id, title)

							link_dict = {
								"id": link.id,
								"title": link.title,
								"url": link.url,
								"domain": link.domain,
								"image_url": link.image_url,
								"embed_url": link.embed_url,
								"embed_type": link.embed_type,
								"screenshot_url": screenshots.get_screenshot(link.url),
								"timesince": utils.timesince(link.date)
							}
							links.append(link_dict)

		result = {
			'success': True,
			'thread_id': thread_id,
			'links': links
		}
	except Exception as error:
		result = {
			'success': False,
			'message': str(error)
		}

	return jsonify(result)


def get_added_chart_data():
	stats = database.get_stats()
	history = stats.get_add_history()[:28]
	output = []

	for i in range(len(history)):
		days_ago = 27 - i
		date = datetime.now() - timedelta(days=days_ago)

		output.append({'date': date.strftime("%Y-%m-%d"), 'added': history[i]})

	return json.dumps(output)


def get_clicked_chart_data():
	stats = database.get_stats()
	history = stats.get_click_history()[:28]
	output = []

	for i in range(len(history)):
		days_ago = 27 - i
		date = datetime.now() - timedelta(days=days_ago)

		output.append({'date': date.strftime("%Y-%m-%d"), 'clicked': history[i]})

	return json.dumps(output)


def get_pageviews_chart_data():
	stats = database.get_stats()
	history = stats.get_view_history()[:28]
	output = []

	for i in range(len(history)):
		days_ago = 27 - i
		date = datetime.now() - timedelta(days=days_ago)

		output.append({'date': date.strftime("%Y-%m-%d"), 'pageviews': history[i]})

	return json.dumps(output)


def notifications():
	unread_links = database.get_matching_links(unread=True, starred=False, archived=False)
	result = {
		'success': True,
		'value': len(unread_links)
	}
	return jsonify(result)


def ping():
	result = { 'success': True }
	return jsonify(result)


def star(id):
	result = { }

	try:
		link = database.get_link_by_id(id)
		if link.unread:
			result['moved_from_inbox'] = True
			result['moved_from_archive'] = False
		else:
			result['moved_from_inbox'] = False
			result['moved_from_archive'] = True

		database.mark_link_as_starred(id)
		database.unarchive_link(id)
		result['success'] = True
	
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def title(id, new_title):
	result = { }

	try:
		database.edit_title(id, new_title)
		result = { 'success': True, 'title': new_title }

	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def unarchive(id):
	result = { }

	try:
		database.unarchive_link(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def unstar(id):
	result = { }

	try:
		database.mark_link_as_unstarred(id)
		link = database.get_link_by_id(id)
		if link.unread:
			result['moved_to_archive'] = False
			result['moved_to_inbox'] = True
		else:
			result['moved_to_archive'] = True
			result['moved_to_inbox'] = False
			database.archive_link(id)
		result['success'] = True
	
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)

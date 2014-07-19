from datetime import datetime
from flask import jsonify
from utils import utils
from external_apis import screenshots
from model import database

def add(url, title=''):
	result = { }

	if len(url) > 0:
		if utils.page_exists(url):
			try:
				link = database.add_link(url, datetime.now())
				if title and (len(title) > 0):
					database.edit_title_without_counting(link.id, title)
	
			except Exception as error:
				print "(API) Couldn't add link. " + str(type(error)) + " - " + str(error)
				result = { 'success': False, 'valid_url': True, 'message': str(error) }

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
					'screenshot_url': screenshots.get_screenshot(link.url)
				}
			}

		else:
			result = { 'success': False, 'valid_url': utils.page_exists(url), 'no_url': False }

	else:
		result = { 'success': False, 'valid_url': False, 'no_url': True}

	return jsonify(result)


def archive(id):
	result = { }

	try:
		database.archive_link(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': error }

	return jsonify(result)


def click(id):
	result = { }

	try:
		database.mark_link_as_read(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': error }

	return jsonify(result)


def delete(id):
	result = { }

	try:
		database.delete_link(id)
		result = { 'success': True }
	except Exception as error:
		result = { 'success': False, 'message': error }

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
			'message': error
		}

	return jsonify(result)


def star(id):
	result = { }

	try:
		result = database.mark_link_as_starred(id)
		result = { 'success': result }
	
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
		result = { 'success': False, 'message': error }

	return jsonify(result)


def unstar(id):
	result = { }

	try:
		database.mark_link_as_unstarred(id)
		result = { 'success': True }
	
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)

from datetime import datetime
from flask import jsonify
import utils
from external_apis import screenshots

import database

def add(url, title=''):
	result = { }

	if len(url) > 0:
		if utils.page_exists(url):
			try:
				link = database.add_link(url, datetime.now())
				if title and (len(title) > 0):
					database.edit_title(link.id, title)
	
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


def star(id):
	result = { }

	try:
		result = database.mark_link_as_starred(id)
		result = { 'success': result }
	
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)


def unstar(id):
	result = { }

	try:
		database.mark_link_as_unstarred(id)
		result = { 'success': True }
	
	except Exception as error:
		result = { 'success': False, 'message': str(error) }

	return jsonify(result)
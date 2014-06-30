from datetime import datetime
from flask import jsonify
import utils

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

			result = { 'success': True, 'valid_url': True, 'link': { 'id': link.id, 'title': link.title, 'url': link.url } }

		else:
			result = { 'success': False, 'valid_url': utils.page_exists(url), 'no_url': False }

	else:
		result = { 'success': False, 'valid_url': False, 'no_url': True}

	return jsonify(result)

from datetime import datetime
from flask import jsonify

import database

def add(url, title=''):
	try:
		link = database.add_link(url, datetime.now())
		if title and (len(title) > 0):
			database.edit_title(link.id, title)
	
	except Exception as error:
		print "(API) Couldn't add link. " + str(type(error)) + " - " + str(error)
		result = { 'success': False, 'message': str(error) }
		return jsonify(result)

	result = { 'success': True, 'link': { 'id': link.id, 'title': link.title, 'url': link.url } }
	return jsonify(result)
import requests

def _make_request(url):
	api_url = 'http://s.wordpress.com/mshots/v1/{0}'.format(url)
	response = requests.get(api_url)
	if (response.ok):
		return response
	else:
		return None

def get_screenshot(url):
	response = _make_request(url)
	if not (response is None):
		headers = response.headers
		if 'image/gif' in headers['content-type']:
			return 'http://s.wordpress.com/mshots/v1/http://linkbucket.joshasch.com'
		else:
			return 'http://s.wordpress.com/mshots/v1/{0}'.format(url)
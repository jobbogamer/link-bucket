from urlparse import urlparse
import requests

def find_domain(url):
	parsed_url = urlparse(url)
	if len(parsed_url.scheme) > 0:
		return parsed_url.hostname.replace('www.', '')
	else:
		return urlparse('//' + url).hostname.replace('www.', '')

def page_exists(url):
	try:
		response = requests.get(url)
		return response.ok
	except:
		return False
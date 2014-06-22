import requests
import json

__token = 'ce41e71c9a5063a8d4ca8b41a9c22eda4b449668'

class Page():
	url = ''
	domain = ''
	title = ''
	excerpt = ''
	word_count = 0
	image_url = ''

	def __init__(self, json_page):
		self.url = json_page['url']
		self.domain = json_page['domain'].replace('www.', '')
		self.title = json_page['title']
		self.author = json_page['author']
		self.excerpt = json_page['excerpt']
		self.word_count = json_page['word_count']
		self.image_url = json_page['lead_image_url']

def _make_request(url):
	api_url = 'http://readability.com/api/content/v1/parser?url={0}&token={1}'.format(url, __token)
	response = requests.get(api_url)
	if (response.ok):
		result = json.loads(response.text or response.content)
		return result
	else:
		return None

def parse(url):
	result = _make_request(url)
	if (result is None) or ('error' in result):
		return None
	else:
		return Page(result)
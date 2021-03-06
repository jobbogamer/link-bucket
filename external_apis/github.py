import requests
import json
from datetime import datetime
from utils import utils

class Commit():
	sha1 = ''
	author = ''
	date = None
	message = ''
	url = ''
	
	def __init__(self, json_commit):
		self.sha1 = json_commit['sha']
		self.author = json_commit['commit']['author']['name']
		self.date = datetime.strptime(json_commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
		self.message = json_commit['commit']['message']
		self.url = json_commit['html_url']

class Tag():
	name = ''
	commit_url = ''

	def __init__(self, json_tag):
		self.name = json_tag['name']
		self.commit_url = json_tag['commit']['url']

class Release():
	tag_name = ''
	body = ''
	date = None
	url = ''

	def __init__(self, json_release):
		self.tag_name = json_release['tag_name']
		self.body = json_release['body']
		self.date = utils.parse_date(json_release['created_at'])
		self.url = json_release['html_url']
		

def _make_request(endpoint):
	url = "https://api.github.com/" + endpoint
	response = requests.get(url)
	if (response.ok):
		result = json.loads(response.text or response.content)
		return result
	else:
		return None

def get_tags(owner, repo):
	return _make_request('repos/{0}/{1}/tags'.format(owner, repo))

def get_last_tag(owner, repo):
	tags = get_tags(owner, repo)
	greatest_name = 'v0.0.0'
	latest_tag = None
	if tags is not None:
		for tag in tags:
			if tag['name'] > greatest_name:
				greatest_name = tag['name']
				latest_tag = tag
		return Tag(latest_tag)
	else:
		return None

def get_commits(owner, repo):
	commits = _make_request('repos/{0}/{1}/commits'.format(owner, repo))
	return commits

def get_latest_commit(owner, repo):
	commits = get_commits(owner, repo)
	latest_date = None
	latest_commit = None
	if commits is not None:
		for commit in commits:
			if commit['commit']['author']['date'] > latest_date:
				latest_date = commit['commit']['author']['date']
				latest_commit = commit
		return Commit(latest_commit)
	else:
		return None

def get_releases(owner, repo):
	return _make_request('repos/{0}/{1}/releases'.format(owner, repo))

def get_latest_release(owner, repo):
	releases = get_releases(owner, repo)
	latest_date = None
	latest_release = None
	if releases is not None:
		for release in releases:
			if release['created_at'] > latest_date:
				latest_date = release['created_at']
				latest_release = release
		return Release(latest_release)
	else:
		return None

def get_latest_releases(owner, repo, count):
	releases = get_releases(owner, repo)
	if releases is not None:
		releases = sorted(releases, key=lambda release: release['created_at'], reverse=True)
		releases = releases[:count]
		result = [Release(release) for release in releases]
		return result
	else:
		return None

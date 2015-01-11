from urlparse import urlparse
from datetime import datetime
from time import gmtime, strftime
import requests
import re

def extract_links(string):
	links = []

	regexp = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
	matches = regexp.findall(string)

	if len(matches) > 0:
		for match in matches:
			links.append(match[0])

	return links

def extract_title(string, urls):
	string = string.replace(':rt:', '')

	for url in urls:
		string = string.replace(url, '')

	return string.strip()

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

def parse_date(string):
	date = datetime.strptime(string[0:19], '%Y-%m-%dT%H:%M:%S')
	time_diff = datetime.now() - datetime.utcnow()
	date = date + time_diff
	return date

def reading_time(word_count):
	if word_count is None:
		return ""
	else:
		minutes = int(word_count / 250)

		if minutes < 1:
			return "<1m"
		else:
			return "{0}m".format(minutes)

def timesince(date):
	now = datetime.now()
	delta = now - date
	seconds = delta.total_seconds()

	if seconds < 60:
		return "<1m"
	elif seconds < (60 * 60):
		return str(int(seconds / 60)) + "m"
	elif seconds < (24 * 60 * 60):
		return str(int(seconds / (60 * 60))) + "h"
	else:
		return str(int(seconds / (24 * 60 * 60))) + "d"

def video_duration(seconds):
	hours = int(seconds / 3600)
	leftover_seconds = seconds - (hours * 3600)

	minutes = int(leftover_seconds / 60)
	leftover_seconds -= (minutes * 60)

	if minutes < 10:
		minutes_str = "0{0}".format(minutes)
	else:
		minutes_str = str(minutes)

	if leftover_seconds < 10:
		seconds_str = "0{0}".format(leftover_seconds)
	else:
		seconds_str = str(leftover_seconds)

	if hours > 0:
		return "{0}:{1}:{2}".format(hours, minutes_str, seconds_str)
	else:
		return "{0}:{1}".format(minutes, seconds_str)

def find_domain(url):
	parsed_url = urlparse(url)
	if len(parsed_url.scheme) > 0:
		return parsed_url.hostname.replace('www.', '')
	else:
		return urlparse('//' + url).hostname.replace('www.', '')

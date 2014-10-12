var KEY_BACKSPACE = 8;
var KEY_ENTER = 13;
var KEY_ESCAPE = 27;
var KEY_ARROW_UP = 38;
var KEY_ARROW_DOWN = 40;
var KEY_DELETE = 46;

var searchItems = [];
var searchResults = [];
var selectedItem = -1;
var query = "";
var contactingServer = false;
var queryInserted = false;

function getLinksFromServer() {
	$('.search-static').html('<i class="fa fa-spin fa-spinner"></i>');
	contactingServer = true;
	$.ajax({
		url: '/api/all'
	}).done(function(data) {
		selectedItem = -1;
		searchResults = [];
		contactingServer = false;
		if (data['success']) {
			searchItems = data['links'];
			performSearch(query);
		} else {
			searchItems = [];
			$('.search-static').html('<p>No results.</p>');
		}
	})
}

function hideDropdown() {
	$('#coverup').fadeOut();
	$('#search-results').fadeOut();
}

function markItemSelected(index) {
	if (index <= searchResults.length) {
		$('#search-result-' + selectedItem).removeClass('selected');
		$('#search-result-' + index).addClass('selected');
		selectedItem = index;
	}
}

function openSelectedItem() {
	if (selectedItem > -1) {
		document.getElementById('search-link-' + selectedItem).click();
		// log a click
	}
}

function performSearch(query) {
	selectedItem = -1;
	searchResults = [];
	if (searchItems.length == 0) {
		$('.search-static').html('<p>No results.</p>');
	} else {
		regexString = "";
		for (var i = 0; i < query.length; i++) {
			regexString = regexString + ".*" + query.substring(i, i+1);
		}
		regex = new RegExp(regexString, 'i');
		results = [];
		for (var i = 0; i < searchItems.length; i++) {
			if (regex.test(searchItems[i]["title"])) {
				if (searchResults.length < 10) {
					searchResults.push(searchItems[i]);
				}
			}
		}
		updateResultDropdown();
	}
}

function searchBarBlur(searchBar) {
	hideDropdown();
}

function searchBarFocus(searchBar) {
	if (searchBar.value.length == 0 || queryInserted) {
		getLinksFromServer();
		queryInserted = false;
	} else {
		showDropdown();
	}
}

function searchBarKeyDown(searchBar, event) {
	if (event.keyCode == KEY_ENTER) {
		event.preventDefault();
		if (selectedItem > -1) {
			openSelectedItem();
		} else if (searchBar.value.length > 0) {
			slash = window.location.href.indexOf('/', 7);
			current = window.location.href.substring(0, slash);
			window.location.href = current + "/search?q=" + searchBar.value;
		}
	} else if (event.keyCode == KEY_ESCAPE) {
		event.preventDefault();
		if (searchBar.value.length > 0) {
			searchBar.value = "";
			hideDropdown();
		} else {
			searchBar.blur();
		}
	} else if (event.keyCode == KEY_ARROW_UP) {
		event.preventDefault();
		if (selectedItem > -1) {
			markItemSelected(selectedItem - 1);
		}
	} else if (event.keyCode == KEY_ARROW_DOWN) {
		event.preventDefault();
		if (selectedItem + 1 < searchResults.length) {
			markItemSelected(selectedItem + 1);
		}
	} else if (event.keyCode == KEY_BACKSPACE || event.keyCode == KEY_DELETE) {
		if (searchBar.value.length == 1) {
			hideDropdown();
		}
	}
}

function searchBarKeyPressed(searchBar, event) {
	if (!event.metaKey) {
		var keynum;
		if (window.event) { // IE					
			keynum = event.keyCode;
		} else if (e.which) { // Other browsers					
			keynum = event.which;
		}
		query = searchBar.value + String.fromCharCode(keynum);
		if (query.length > 0) {
			showDropdown();
			if (!contactingServer) {
				performSearch(query);
			}
		} else {
			hideDropdown();
		}
	}
}

function showDropdown() {
	$('#coverup').fadeIn();
	$('#search-results').fadeIn();
}

function updateResultDropdown() {
	if (searchResults.length == 0) {
		html = '<li id="search-result-1">' +
					'<a>' +
						'<div class="search-result-wrapper">' +
							'<div class="search-static">' +
								'<p>No Results.</p>' +
							'</div>' +
						'</div>' +
					'</a>' +
				'</li>';
	} else {
		html = "";
		for (var i = 0; i < searchResults.length && i < 10; i++) {
			itemHTML = '<li id="search-result-' + i + '" onmouseover="markItemSelected(' + i + ');">' +
							'<a onclick="clickLink(' + searchResults[i]["id"] + ');" id="search-link-' + i + '" target="_blank" href="' + searchResults[i]["url"] + '">' +
								'<div class="search-result-wrapper">' + 
									'<p class="title">' + searchResults[i]["title"] + '</p>' +
									'<div class="meta">' +
										'<p class="domain">' + searchResults[i]["domain"] + '</p>' +
										'<p class="date">' + searchResults[i]["date"] + '</p>' +
									'</div>' +
								'</div>' +
							'</a>' +
						'</li>';
			html = html + "\n" + itemHTML;
		}
	}
	$('#search-results ul').html(html);
}

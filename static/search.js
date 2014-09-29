var KEY_ENTER = 13;
var KEY_ESCAPE = 27;
var KEY_ARROW_UP = 38;
var KEY_ARROW_DOWN = 40;

var searchResults = null;
var numResults = 0;
var selectedItem = 0;

function getLinksFromServer() {
	
}

function hideDropdown() {
	$('#coverup').fadeOut();
	$('#search-results').fadeOut();
}

function markItemSelected(index) {
	$('#search-result-' + selectedItem).removeClass('selected');
	$('#search-result-' + index).addClass('selected');
	selectedItem = index;
}

function openSelectedItem() {
	if (selectedItem > 0) {
		href = $('#search-result-' + selectedItem + ' a').attr('href');
		// log a click
		window.location.href = href;
	}
}

function performSearch(query) {

}

function searchBarBlur(searchBar) {
	hideDropdown();
}

function searchBarFocus(searchBar) {
	showDropdown();
}

function searchBarKeyDown(searchBar, event) {
	if (event.keyCode == KEY_ENTER) {
		event.preventDefault();
		if (selectedItem > 0) {
			openSelectedItem();
		} else if (searchBar.value.length > 0) {
			slash = window.location.href.indexOf('/', 7);
			current = window.location.href.substring(0, slash);
			window.location.href = current + "/search?q=" + searchBar.value;
		}
	} else if (event.keyCode == KEY_ESCAPE) {
		if (searchBar.value.length > 0) {
			searchBar.value = "";
		} else {
			searchBar.blur();
		}
	} else if (event.keyCode == KEY_ARROW_UP) {
		if (selectedItem > 0) {
			markItemSelected(selectedItem - 1);
		}
		event.preventDefault();
	} else if (event.keyCode == KEY_ARROW_DOWN) {
		if (selectedItem < numResults) {
			markItemSelected(selectedItem + 1);
		}
		event.preventDefault();
	} else {
		performSearch(searchBar.value);
	}
}

function showDropdown() {
	$('#coverup').fadeIn();
	$('#search-results').fadeIn();
}

function updateResultDropdown() {

}

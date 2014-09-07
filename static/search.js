var KEY_ENTER = 13;
var KEY_ESCAPE = 27;
var KEY_ARROW_UP = 38;
var KEY_ARROW_DOWN = 40;

function searchBarKeyDown(searchBar, event) {
	if (event.keyCode == KEY_ENTER) {

	} else if (event.keyCode == KEY_ESCAPE) {
		// on first press, clear search bar
		// on second press, blur search bar
	} else if (event.keyCode == KEY_ARROW_UP) {
		// highlight next result up
	} else if (event.keyCode == KEY_ARROW_DOWN) {
		// highlight next result down
	}
}

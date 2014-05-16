function archiveItem(id) {
	$.ajax({
		url: '/archive/' + id,
		success: hideArchivedItem(id)
	});
}

function hideArchivedItem(id) {
	$("#item-" + id).fadeOut();
}

function unarchiveItem(id) {
	$.ajax({
		url: '/unarchive/' + id,
		success: hideUnarchivedItem(id)
	});
}

function hideUnarchivedItem(id) {
	$("#item-" + id).fadeOut();
}

function editItem(id) {
	var currentTitle = document.getElementById("title-" + id).innerHTML;
	var response = prompt("Enter a new title for this link:", currentTitle);
	if (response != null && response != '' && response != currentTitle) {
		$.ajax({
			url: '/edit/' + id + "?title=" + response,
			success: showNewTitle(id, response)
		});
	}
}

function showNewTitle(id, newTitle) {
	document.getElementById("title-" + id).innerHTML = newTitle;
}

function searchBarFocus(searchbar) {
	if (searchbar.value == 'Search') {
		searchbar.value='';
		searchbar.style.color='black';
	}
}

function searchBarBlur(searchbar) {
	if (searchbar.value == '') {
		searchbar.value = 'Search';
		searchbar.style.color = '#9F9F9F';
		resetSearch();
	}
}

function searchBarKeyDown(searchbar, event) {
	if (event.keyCode == 13) {
		performSearch(searchbar.value);
	} else if (event.keyCode == 27) {
		searchbar.blur();
		searchbar.value = '';
		searchBarBlur(searchbar);
	}
}

function performSearch(searchTerm) {
	if (searchTerm == '') {
		resetSearch();
	} else {
		var items = document.getElementsByClassName("title");
		for (var i = 0; i < items.length; i++) {
			var element = items[i];
			if (element.innerHTML.toLowerCase().indexOf(searchTerm.toLowerCase()) == -1) {
				element.parentNode.parentNode.style.display = "none";
			} else {
				element.parentNode.parentNode.style.display = "list-item";
			}
		}
	}
}

function resetSearch() {
	var items = document.getElementsByClassName("title");
	for (var i = 0; i < items.length; i++) {
		var element = items[i];
		element.parentNode.parentNode.style.display = "list-item";
	}
}

function showButtons(id, show) {
	var element = document.getElementById('buttons-' + id);
	if (show) {
		element.style.display = "block";
	} else {
		element.style.display = "none";
	}
}

function getTitle() {
	document.getElementById('autotitle').innerHTML = '<i class="fa fa-spin fa-cog"></i>';
	document.getElementById('autotitle').style.color = '#3F3F3F';
	var url = document.getElementById('urlfield').value;
	$.get("/title/" + url, function(data) {
		if (data != '!!!null!!!') {
			document.getElementById('autotitle').innerHTML = '<i class="fa fa-search"></i>';
			document.getElementById('titlefield').value = data;
			document.getElementById('titlefield').style.color = 'black';
			document.getElementById('autotitle').style.color = '#3F3F3F';
		} else {
			document.getElementById('autotitle').innerHTML = '<i class="fa fa-exclamation-circle"></i>';
			document.getElementById('autotitle').style.color = 'red';
		}
	});
}

function showEmbed(id) {
	var html = document.getElementById("show-embedded-" + id).innerHTML;
	if (html.indexOf("plus") > -1) {
		document.getElementById("show-embedded-" + id).innerHTML = '<i class="fa fa-minus-square-o"></i>';
	} else {
		document.getElementById("show-embedded-" + id).innerHTML = '<i class="fa fa-plus-square-o"></i>';
	}
	$("#embedded-" + id).slideToggle();
}

function showAchievements(achievements) {
	var html = "";
	for (var i = 0; i < achievements.length; i++) {
		var achievement = achievements[i];
		html += '<li class="notification ' + achievement.difficulty + '">' +
					'<i class="fa-li fa fa-trophy"></i>' +
					'Achievement Unlocked: ' + achievement.name +
					'</li>\n';
	}
	var ul = document.getElementById('unlocked-achievements');
	ul.innerHTML = html;

	if (achievements.length > 0) {
		ul.style.border = "1px solid #9F9F9F";
	} else {
		ul.style.border = "none";
	}
}

function clickItem(id) {
	$.ajax({
		url: '/click/' + id,
	}).done(function(data) {
		showAchievements(data.achievements);
		hideUnreadIndicator(id);
	});
}

function archiveItem(id) {
	$.ajax({
		url: '/archive/' + id,
		success: hideArchivedItem(id)
	}).done(function(data) {
		showAchievements(data.achievements);
	});
}

function hideArchivedItem(id) {
	$("#item-" + id).fadeOut();
}

function unarchiveItem(id) {
	$.ajax({
		url: '/unarchive/' + id,
		success: hideUnarchivedItem(id)
	}).done(function(data) {
		showAchievements(data.achievements);
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
		}).done(function(data) {
			showAchievements(data.achievements);
		});
	}
}

function showNewTitle(id, newTitle) {
	document.getElementById("title-" + id).innerHTML = newTitle;
}

function starItem(id) {
	$.ajax({
		url: '/star/' + id,
		success: showStarIndicator(id)
	});
}

function unstarItem(id) {
	$.ajax({
		url: '/unstar/' + id,
		success: hideStarIndicator(id)
	});
}

function showStarIndicator(id) {
	$('#item-' + id).addClass("starred");
}

function hideStarIndicator(id) {
	$('#item-' + id).removeClass("starred");
}

function hideUnreadIndicator(id) {
	$('#item-' + id).removeClass("unread");
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

function searchBarKeyDown(searchbar, event, archive) {
	if (event.keyCode == 13) {
		performSearch(searchbar.value, archive);
	} else if (event.keyCode == 27) {
		searchbar.blur();
		searchbar.value = '';
		searchBarBlur(searchbar);
	}
}

function performSearch(searchTerm, archive) {
	if (searchTerm == '') {
		resetSearch();
	} else {
		var url = archive ? '/searcharchive/' + searchTerm : '/search/' + searchTerm;
		var result = $.ajax({
			url: url
		}).done(function(data) {
			var matched = data.matched;
			var notMatched = data.not_matched;

			for (var i = 0; i < matched.length; i++) {
				document.getElementById("item-" + matched[i]).className =
					document.getElementById("item-" + matched[i]).className.replace('notMatched', 'matched');
			}

			for (var i = 0; i < notMatched.length; i++) {
				document.getElementById("item-" + notMatched[i]).className = 
					document.getElementById("item-" + notMatched[i]).className.replace('matched', 'notMatched');
			}

			$('.notMatched').slideUp();
			$('.matched').slideDown();

			showAchievements(data.achievements);
		});
	}
}

function resetSearch() {
	var items = document.getElementsByClassName("item");
	for (var i = 0; i < items.length; i++) {
		var element = items[i];
		element.className = element.className.replace('notMatched', 'matched');
	}

	$('.matched').slideDown();
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
		clickItem(id);
	} else {
		document.getElementById("show-embedded-" + id).innerHTML = '<i class="fa fa-plus-square-o"></i>';
	}
	$("#embedded-" + id).slideToggle();
}

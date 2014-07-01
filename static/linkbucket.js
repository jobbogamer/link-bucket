$(function() {
	getViewModeFromCookie();
	setUpModals();
	setUpPopovers();
});

function addLinkFromModal() {
	hideAddError();
	document.getElementById('add-modal-add-button').innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
	document.getElementById('add-modal-add-button').disabled = true;
	document.getElementById('add-modal-cancel-button').disabled = true;
	var url = document.getElementById('add-modal-url-field').value;
	var title = document.getElementById('add-modal-title-field').value;
	$.ajax({
		url: '/api/add',
		data: {
			'url' : url,
			'title': title
		}
	}).done(function(data) {
		if (data['success']) {
			$('#add-modal').modal('hide');
		} else {
			if (data['valid_url']) {
				var error = data['message'];
				showAddError(true, true, error);
			} else if (data['no_url']) {
				showAddError(false, true, '');
			} else {
				showAddError(true, false, '');
			}
		}
	}).always(function(data) {
		document.getElementById('add-modal-add-button').innerHTML = 'Add';
		document.getElementById('add-modal-add-button').disabled = false;
		document.getElementById('add-modal-cancel-button').disabled = false;
	});
}

function getViewModeFromCookie() {
	var viewMode = $.cookie('viewmode');
	if (viewMode == "compact") {
		setCompactMode(true);
	} else if (viewMode == "expanded") {
		setCompactMode(false);
	}
}

function hideAddError() {
	$('#add-modal-error-message').slideUp();
}

function hideNavbarDropdown() {
	$('#navbar-collapse').collapse('hide');
}

function setCompactMode(compact) {
	if (compact) {
		$('body').addClass('compact');
		$('#viewmode-expanded').removeClass('active');
		$('#viewmode-compact').addClass('active');
		document.getElementById('viewmode-mobile').innerHTML = 'Expanded View';
		setViewModeCookie(true);
	} else {
		$('body').removeClass('compact');
		$('#viewmode-expanded').addClass('active');
		$('#viewmode-compact').removeClass('active');
		document.getElementById('viewmode-mobile').innerHTML = 'Compact View';
		setViewModeCookie(false);
	}
}

function setUpEmbedPopover(id, embedType, url, originalURL) {
	var title = document.getElementById('title-' + id).innerHTML;
	document.getElementById('embed-modal-title').innerHTML = '<a href="' + originalURL + '">' + title + '</a>';
	if (embedType == 1) {
		var html = '<div class="video-wrapper"><iframe src="' + url + '?rel=0" frameborder="0" allowfullscreen="true"></iframe></div>';
		document.getElementById('embed-modal-body').innerHTML = html;
	} else if (embedType == 2) {
		var html = '<img src="' + url + '" />'
		document.getElementById('embed-modal-body').innerHTML = html;
	}
}

function setUpModals() {
	$('#add-modal').on('hidden.bs.modal', function (e) {
  		hideAddError();
	})
}

function setUpPopovers() {
	$('#add-modal-error-popover').popover({
		placement: "bottom",
		template: '<div class="popover" role="tooltip"><div class="arrow"></div><div class="popover-content"></div></div>',
	});
}

function setViewModeCookie(compact) {
	var mode = compact ? "compact" : "expanded";
	$.cookie('viewmode', mode, { expires: 365, path: '/' });
}

function showAddError(urlGiven, validURL, databaseError) {
	if (!urlGiven) {
		document.getElementById('add-modal-error-title').innerHTML = "You forgot something.";
		document.getElementById('add-modal-error-content').innerHTML = "No URL was given.";
	} else if (!validURL) {
		document.getElementById('add-modal-error-title').innerHTML = "That's not the link you're looking for.";
		document.getElementById('add-modal-error-content').innerHTML = "It doesn't look like that URL points to a valid page.";
	} else {
		document.getElementById('add-modal-error-title').innerHTML = "Something went wrong.";
		document.getElementById('add-modal-error-content').innerHTML = 'That link couldn\'t be added; try again later. <a id="add-modal-error-popover" data-toggle="popover" data-content="' + databaseError + '">What was the error?</a>';
	}
	$('#add-modal-error-message').slideDown();
}

function toggleCompactMode() {
	if ($('body').hasClass('compact')) {
		setCompactMode(false);
	} else {
		setCompactMode(true);
	}
}
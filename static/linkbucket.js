$(function() {
	getViewModeFromCookie();
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
		url: '/add',
		data: {
			'url' : url,
			'title': title
		}
	}).done(function(data) {
		var success = data['success'];
		if (success) {
			$('#add-modal').modal('hide');
		} else {
			var error = data['message'];
			showAddError(error);
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

function showAddError(error) {
	document.getElementById('add-modal-error-popover').dataset.content = error;
	$('#add-modal-error-message').slideDown();
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
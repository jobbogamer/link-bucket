$(function() {
	setUpPopovers();
});

function addLinkFromModal() {
	hideAddError();
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
	});
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

function showAddError(error) {
	document.getElementById('add-modal-error-popover').dataset.content = error;
	$('#add-modal-error-message').slideDown();
}

function toggleCompactMode() {
	$('body').toggleClass('compact');
}
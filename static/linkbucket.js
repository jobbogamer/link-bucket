function addLinkFromModal() {
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
			console.log('oopsie, something went wrong');
		}
	});
}

function hideNavbarDropdown() {
	$('#navbar-collapse').collapse('hide');
}

function toggleCompactMode() {
	$('body').toggleClass('compact');
}
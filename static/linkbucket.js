$(function() {
	facebookLoadSDK();
	getViewModeFromCookie();
	setUpModals();
	setUpTooltips();
	setUpPopovers();
	showAddSheetIfNecessary();
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
			var link = data['link'];
			createAddedLink(link['id'], link['url'], link['title'], link['domain'], link['embed_type'], link['embed_url'], link['image_url'], link['screenshot_url']);
			clearAddModal();
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

function archiveLink(id) {
	$.ajax({
		url: '/api/archive',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			$('#link-' + id).fadeOut(complete = function() {
				$('#link-' + id).parent().remove();
			});	
		}
	});
}

function clearAddModal() {
	document.getElementById('add-modal-url-field').value = "";
	document.getElementById('add-modal-title-field').value = "";
}

function clickLink(id) {
	$.ajax({
		url: '/api/click',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			$('#link-' + id).removeClass('unread');	
		}
	})
}

function createAddedLink(id, url, title, domain, embedType, embedURL, imageURL, screenshotURL) {
	if (embedType > 0) {
		var aTag = '<a class="embed-link" data-toggle="modal" data-target="#embed-modal"' +
						'onclick="setUpEmbedPopover(' + id + ', ' + embedType + ', \'' + embedURL + '\', \'' + url + '\');">';
	} else {
		var aTag = '<a target="_blank" href="' + url + '">';
	}

	if (showImages) {
		if (imageURL) {
			var thumbnail = '<span class="thumbnail" style="background-image: url(\'' + imageURL + '\');"></span>';
		} else {
			if (embedType == 2) {
				var thumbnail = '<span class="thumbnail image-embed" style="background-image: url(\'' + embedURL + '\');"></span>';
			} else {
				var thumbnail = '<span class="thumbnail screenshot" style="background-image: url(\'' + screenshotURL + '\');"></span>';
			}
		}
	} else {
		var thumbnail = '';
	}

	if (embedType == 1) {
		var indicator = '<i class="indicator embed-indicator fa fa-film"></i>';
	} else if (embedType == 2) {
		var indicator = '<i class="indicator embed-indicator fa fa-image"></i>';
	} else {
		var indicator = '<i class="indicator unread-indicator fa fa-circle"></i><i class="indicator starred-indicator fa fa-star"></i>';
	}

	var html = '<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3">' +
					'<div id="link-' + id + '" class="link unread">' +
						aTag +
							'<p id="title-' + id + '" class="title">' + title + '</p>' + 
							thumbnail +
							'<div class="meta">' +
								indicator +
								'<p class="domain">' + domain + '</p>' +
								'<time>&lt;1m</time>' +
								'<div class="buttons">' +
									'<a onclick="archiveLink(' + id + ');"><i class="button fa fa-trash-o"></i></a>' +
									'<a><i class="button fa fa-pencil"></i></a>' +
									'<a onclick="toggleStar(' + id + ');"><i id="star-button-' + id + '" class="button star-button fa fa-star"></i></a>' +
								'</div>' +
							'</div>' +
						'</a>' +
					'</div>' +
				'</div>';

	$('.row').prepend(html);
}

function deleteLink(id) {
	$.ajax({
		url: '/api/delete',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			$('#link-' + id).fadeOut(complete = function() {
				$('#link-' + id).parent().remove();
			});	
		}
	});
}

function editTitleFromModal() {
	var id = document.getElementById('edit-modal-save-button').dataset.id;
	$.ajax({
		url: '/api/title',
		data: {
			'id' : id,
			'title': document.getElementById('edit-modal-title-field').value
		}
	}).done(function(data) {
		if (data['success']) {
			document.getElementById('title-' + id).innerHTML = data['title'];
			$('#edit-modal').modal('hide');
		}
	});
}

function getURLParameters() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = decodeURIComponent(hash[1]);
    }
    return vars;
}

function getViewModeFromCookie() {
	if (showImages) {
		var viewMode = $.cookie('viewmode');
		if (viewMode == "compact") {
			setCompactMode(true);
		} else if (viewMode == "expanded") {
			setCompactMode(false);
		}
	} else {
		var viewMode = "compact";
		setCompactMode(true);
	}
}

function hideAddError() {
	$('#add-modal-error-message').slideUp();
}

function hideFacebookError() {
	$('#facebook-modal-error-message').slideUp();
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
	});

	$('#add-modal').on('shown.bs.modal', function (e) {
  		$('#add-modal-url-field').focus();
	});

	$('#edit-modal').on('shown.bs.modal', function (e) {
		$('#edit-modal-title-field').focus();
	});

	$('#facebook-modal').on('hidden.bs.modal', function (e) {
		hideFacebookError();
	});
}

function setUpPopovers() {
	$('#add-modal-error-popover').popover({
		placement: "bottom",
		template: '<div class="popover" role="tooltip"><div class="arrow"></div><div class="popover-content"></div></div>',
	});

	$('#version-popover').popover({
		placement: "top",
	})
}

function setUpStatsChart(addHistory, clickHistory) {
	var labels = [];

	for (var i = 0; i < 28; i++) {
		if (i == 27) {
			labels[i] = "Today";
		} else if (i == 26) {
			labels[i] = "Yesterday";
		} else {
			var date = new Date();
			var dayOfMonth = date.getDate();
			date.setDate(dayOfMonth - (27-i));
			var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
			labels[i] = date.getDate() + " " + monthNames[date.getMonth()];
		}
	}

	var max = -1;
	for (var i = 0; i < 28; i++) {
		if (addHistory[i] > max) {
			max = addHistory[i];
		}
		if (clickHistory[i] > max) {
			max = clickHistory[i];
		}
	}

	var data = {
		labels: labels,
		datasets: [{
			label: "Links added",
			fillColor: "RGBA(0, 189, 131, 0)",
			strokeColor: "#00BD83",
			pointColor: "#00BD83",
			pointStrokeColor: "#00BD83",
			pointHighlightFill: "#00BD83",
			pointHighlightStroke: "#00BD83",
			data: addHistory
		},
		{
			label: "Links clicked",
			fillColor: "RGBA(9, 143, 96, 0)",
			strokeColor: "#007A42",
			pointColor: "#007A42",
			pointStrokeColor: "#007A42",
			pointHighlightFill: "#007A42",
			pointHighlightStroke: "#007A42",
			data: clickHistory
		}]
	};

	var context = $("#stats-chart").get(0).getContext("2d");
	var statsChart = new Chart(context).Line(data, {
		responsive: true,
		scaleShowGridLines : false,
		bezierCurve : false,
		bezierCurveTension : 0.4,
		pointDot : false,
		tooltipTitleFontStyle: "normal",
		scaleOverride: true,
		scaleSteps: 1,
    	scaleStepWidth: max,
    	scaleStartValue: 0,
	});

	var legendHTML = statsChart.generateLegend();
	$('.chart-wrapper').append(legendHTML);
}

function setUpTooltips() {
	$('#facebook-login-wrapper').tooltip();
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

function showAddSheetIfNecessary() {
	var params = getURLParameters();
	if (params['add']) {
		if (params['url']) {
			document.getElementById('add-modal-url-field').value = params['url'];
		}
		if (params['title']) {
			document.getElementById('add-modal-title-field').value = params['title'];
		}
		$('#add-modal').modal('show');
	}
}

function showEditTitleModal(id) {
	var title = document.getElementById('title-' + id).innerHTML;
	document.getElementById('edit-modal-title-field').value = title;
	document.getElementById('edit-modal-save-button').dataset.id = id;
}

function showFacebookError() {
	$('#facebook-modal-error-message').slideDown();
}

function toggleCompactMode() {
	if ($('body').hasClass('compact')) {
		setCompactMode(false);
	} else {
		setCompactMode(true);
	}
}

function toggleStar(id) {
	if ($('#link-' + id).hasClass('starred')) {
		var url = '/api/unstar';
	} else {
		var url = '/api/star';
	}
	$.ajax({
		url: url,
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			$('#link-' + id).toggleClass('starred');
		}
	});
}

function unarchiveLink(id) {
	$.ajax({
		url: '/api/unarchive',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			$('#link-' + id).fadeOut(complete = function() {
				$('#link-' + id).parent().remove();
			});	
		}
	});
}

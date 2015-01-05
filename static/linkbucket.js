$(function() {
	facebookLoadSDK();
	setUpModals();
	setUpTooltips();
	setUpPopovers();
	showAddSheetIfNecessary();

	if (activePage == 3) {
		setUpStatsChart();
	}
});

////////// Interaction functions //////////

function clickLink(id) {
	$.ajax({
		url: '/api/click',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			hideLink(id);
			if (data['moved_to_archive']) {
				updateInboxCounter(-1);
				updateArchiveCounter(1);
			}
		} else {
			console.log("Failed to log click");
			console.log(data);
		}
	});
}

function createAddedLink(id, url, title, domain, embedType, embedURL, imageURL, screenshotURL) {
	if (activePage == 0) {
		if (embedType > 0) {
			var aTag = '<!-- Link with some kind of embedded item -->' +
                		'<a class="embed-link"' +
                   			'data-toggle="modal"' +
                   			'data-target="#embed-modal"' +
                   			'onclick="clickLink(' + id + '); setUpEmbedPopover(' + id + ', ' + embedType + ", '" + embedURL + "', '" + url + ');">';
		} else {
			var aTag = '<!-- Normal link with no embedded item -->' +
                	   	'<a target="_blank"' +
                   	   		'href="' + url + '"' +
                   			'onclick="clickLink(' + id + ');">';
		}

		if (embedType == 1) {
			var indicator = '<!-- Filmstrip icon for videos -->' +
                        	'<i class="indicator embed-indicator fa fa-fw fa-film"></i>';
		} else if (embedType == 2) {
			var indicator = '<!-- Photo icon for images -->' +
                        	'<i class="indicator embed-indicator fa fa-fw fa-image"></i>';
		} else {
			var indicator = '<!-- Icon for unread -->' +
                        	'<i class="indicator unread-indicator fa fa-fw fa-circle"></i>';
		}


		var html = '<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3">' +
						'<div id="link-' + id + '"' +
                 			  'class="link unread">' +
                			aTag +
								'<!-- Title of the link -->' +
                    			'<p id="title-' + id + '" class="title">' + title + '</p>' +

                    			'<!-- Meta section with icons, timesince, etc -->' +
                    			'<div class="meta">' +

                    				indicator +

                        			'<!-- Domain name -->' +
                        			'<p class="domain">' + domain + '</p>' +

                        			'<!-- Time since the link was added -->' +
                        			'<time>&lt;1m</time>' +

                        			'<!-- Archive/star/delete buttons -->' +
                        			'<div class="buttons">' +

                            			'<!-- Pencil button for edit -->' +
			                            '<a onclick="showEditTitleModal(' + id + ');"' +
			                               'class="edit-button"' +
			                               'data-toggle="modal"' +
			                               'data-target="#edit-modal">' +

                                			'<i class="button fa fa-fw fa-pencil"></i>' +

                            			'</a> <!-- .edit-button -->' +

			                            '<!-- Star button for star -->' +
			                            '<a onclick="starLink(' + id + ');"' +
			                               'class="star-button">' +

			                                '<i class="button fa fa-fw fa-star"></i>' +

			                            '</a><!-- .star-button -->' +

			                        '</div> <!-- .buttons -->' +

			                    '</div> <!-- .meta -->' +

			                '</a>' +

			            '</div> <!-- #link-xx -->' +

			        '</div> <!-- .col-xs-12 etc -->';

		$('.row').prepend(html);
		updateInboxCounter(1);
	}
}

function deleteLink(id) {
	$.ajax({
		url: '/api/delete',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			hideLink(id);
			updateArchiveCounter(-1);
		} else {
			console.log("Failed to delete link");
			console.log(data);
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

function hideLink(id) {
	$('#link-' + id).fadeOut(complete = function() {
		$('#link-' + id).parent().remove();
	});	
}

function starLink(id) {
	$.ajax({
		url: '/api/star',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			hideLink(id);
			updateStarredCounter(1);
			if (data['moved_from_inbox']) {
				updateInboxCounter(-1);
			} else if (data['moved_from_archive']) {
				updateArchiveCounter(-1);
			}
		} else {
			console.log("Failed to star link");
			console.log(data);
		}
	});
}

function unstarLink(id) {
	$.ajax({
		url: '/api/unstar',
		data: {
			'id' : id
		}
	}).done(function(data) {
		if (data['success']) {
			hideLink(id);
			updateStarredCounter(-1);
			if (data['moved_to_inbox']) {
				updateInboxCounter(1);
			} else if (data['moved_to_archive']) {
				updateArchiveCounter(1);
			}
		} else {
			console.log("Failed to unstar link");
			console.log(data);
		}
	});
}

////////// Counters //////////

function updateCounter(counter, amount) {
	currentCount = $('#' + counter + ' .count').html();
	newCount = parseInt(currentCount) + amount;
	$('#' + counter + ' .count').html(newCount);
}

function updateInboxCounter(amount) {
	updateCounter('inbox-link', amount);
}

function updateStarredCounter(amount) {
	updateCounter('starred-link', amount);
}

function updateArchiveCounter(amount) {
	updateCounter('archive-link', amount);
}

////////// Modals //////////

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

function clearAddModal() {
	document.getElementById('add-modal-url-field').value = "";
	document.getElementById('add-modal-title-field').value = "";
}

function hideAddError() {
	$('#add-modal-error-message').slideUp();
}

function hideFacebookError() {
	$('#facebook-modal-error-message').slideUp();
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

////////// Popovers //////////

function setUpEmbedPopover(id, embedType, url, originalURL) {
	var title = document.getElementById('title-' + id).innerHTML;
	document.getElementById('embed-modal-title').innerHTML = '<a target="_blank" href="' + originalURL + '">' + title + '</a>';
	if (embedType == 1) {
		var html = '<div class="video-wrapper"><iframe src="' + url + '?rel=0" frameborder="0" allowfullscreen="true"></iframe></div>';
		document.getElementById('embed-modal-body').innerHTML = html;
	} else if (embedType == 2) {
		var html = '<img src="' + url + '" />'
		document.getElementById('embed-modal-body').innerHTML = html;
	}
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

////////// Tooltips //////////

function setUpTooltips() {
	$('#facebook-login-wrapper').tooltip();
}

////////// Charts //////////

function setUpStatsChart() {
	d3.json('/api/chart/added', function(data) {
    	data = MG.convert.date(data, 'date');
	    MG.data_graphic({
	        title: "Links Added",
	        data: data,
	        target: '#added-chart',
	        x_accessor: 'date',
	        y_accessor: 'added',
	        interpolate: 'linear',
	        area: false,
	        linked: true,
	        left: 32,
	        right: 32,
	        top: 32,
	        bottom: 32,
	        height: 175,
	        mouseover: function(d, i) {
                var df = d3.time.format('%b %d');
                var date = df(d['date']);
                $('#added-chart svg .mg-active-datapoint')
                    .text(date + '  •  ' + d['added'] + ' added');
            },
    	});
	});

	d3.json('/api/chart/clicked', function(data) {
    	data = MG.convert.date(data, 'date');
	    MG.data_graphic({
	        title: "Links Clicked",
	        data: data,
	        target: '#clicked-chart',
	        x_accessor: 'date',
	        y_accessor: 'clicked',
	        interpolate: 'linear',
	        area: false,
	        linked: true,
	        left: 32,
	        right: 32,
	        top: 32,
	        bottom: 32,
	        height: 175,
	        mouseover: function(d, i) {
                var df = d3.time.format('%b %d');
                var date = df(d['date']);
                $('#clicked-chart svg .mg-active-datapoint')
                    .text(date + '  •  ' + d['clicked'] + ' clicked');
            },
    	});
	});

	d3.json('/api/chart/pageviews', function(data) {
    	data = MG.convert.date(data, 'date');
	    MG.data_graphic({
	        title: "Pageviews",
	        data: data,
	        target: '#pageviews-chart',
	        x_accessor: 'date',
	        y_accessor: 'pageviews',
	        interpolate: 'linear',
	        area: false,
	        linked: true,
	        left: 32,
	        right: 32,
	        top: 32,
	        bottom: 32,
	        height: 175,
	        mouseover: function(d, i) {
                var df = d3.time.format('%b %d');
                var date = df(d['date']);
                $('#pageviews-chart svg .mg-active-datapoint')
                    .text(date + '  •  ' + d['pageviews'] + ' pageviews');
            },
    	});
	});
}

////////// Utilities //////////

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

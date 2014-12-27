function facebookCallbackLoginStatusChanged(response) {
	if (response['status'] === "connected") {
		var userID = response['authResponse']['userID'];
		facebookGetInbox(userID);
	} else {
		$('#facebook-button').prop('disabled', true);
	}
}

function facebookGetOlderMessages(url, threadID, name, lastID, mostRecentID, messages, count) {
	FB.api(url, function(response) {
		var foundLastID = false;
		if (response['comments']) {
			var comments = response['comments']['data'];
			for (var i = 0; i < comments.length; i++) {
				var comment = comments[i];
				if (comment['id'] === lastID) {
					foundLastID = true;
				} else if (comment['id'] > lastID) {
					if (comment['id'] > mostRecentID) {
						mostRecentID = comment['id'];
					}
					messages.push({
						id: comment['id'],
						text: comment['message'],
						date: comment['created_time']
					});
				}
			}
			if (foundLastID || count >= 20) {
				var jsonString = JSON.stringify(messages);
				facebookSendMessagesForParsing(jsonString, threadID, mostRecentID, name);
			} else {
				var nextURL = response['comments']['paging']['next'];
				var threadIDPos = nextURL.indexOf(threadID);
				nextURL = nextURL.substring(threadIDPos);
				facebookGetOlderMessages(nextURL, threadID, lastID, mostRecentID, messages, count+1);
			}
		} else {
			// No messages came back
			console.log(response);
			var listItem = $("#conversation-" + threadID + " .name");
			listItem.html(name);
			showFacebookError();
		}
	});
}

function facebookBeginParseFlow() {
	$('#facebook-button span').toggleClass('fa-facebook');
	$('#facebook-button span').toggleClass('fa-spinner');
	$('#facebook-button span').toggleClass('fa-spin');
	FB.getLoginStatus(function(response) {
		if (response.status === 'connected') {
			var userID = response['authResponse']['userID'];
			facebookGetInbox(userID);
		} else {
			facebookLogIn();
		}
	});
}

function facebookLogIn() {
	FB.login(function(response) {
		if (response['status'] === "connected") {
			var userID = response['authResponse']['userID'];
			facebookGetInbox(userID);
		} else {
			// Don't bother, they obviously don't care
			$('#facebook-button span').toggleClass('fa-facebook');
			$('#facebook-button span').toggleClass('fa-spinner');
			$('#facebook-button span').toggleClass('fa-spin');
		}
	},
	{
		scope: 'read_mailbox'
	});
}

function facebookGetInbox(userID) {
	FB.api('/me/inbox', function(response) {
		var threads = response['data'];
		if (threads) {
			var conversations = [];
			for (var i = 0; i < threads.length; i++) {
				var thread = threads[i];

				var people = [];
				var to = thread['to']['data'];
				for (var person = 0; person < to.length; person++) {
					if (to[person]['id'] !== userID) {
						people.push(to[person]['name']);
					}
				}

				conversations.push({
					id: thread['id'],
					people: people
				});
			}

			if (conversations.length > 0) {
				var html = '<div id="facebook-modal-error-message" class="alert alert-danger">' +
				    	   		'<h4 id="facebook-modal-error-title">Something went wrong.</h4>' +
				    			'<p id="facebook-modal-error-content">Couldn\'t load messages from Facebook; try again later.</p>' +
				    		'</div>' +
				    		'<ul id="conversation-list">';
				var numConversations = Math.min(conversations.length, 10);
				for (var i = 0; i < numConversations; i++) {
					conversation = conversations[i];
					html += '<li id="conversation-' + conversation["id"] +
						'" class="conversation" onclick="facebookParseConversation(' +
						conversation["id"] + ');"><div class="profile-picture">' +
						'<div class="no-picture"></div></div><div class="name">';
					if (conversation['people'].length == 1) {
						html += conversation['people'][0];
					} else if (conversation['people'].length == 2) {
						html += conversation['people'][0] + " and  " + conversation['people'][1];
					} else if (conversation['people'].length == 3) {
						html += conversation['people'][0] + ", " + conversation['people'][1] + ", and " + conversation['people'][2];
					} else {
						html += conversation['people'][0] + ", " + conversation['people'][1] + ", and " + (conversation['people'].length - 1) + " others";
					}
					html += "</div></li>";
				}
				html += "</ul>";
			} else {
				var html = '<div id="empty-conversation-list">No Conversations</div>';
			}

			$('#facebook-modal-body').html(html);
			$('#facebook-modal').modal('show');
			document.getElementById('facebook-button').onclick = facebookToggleConversationList;
			$('#facebook-button span').toggleClass('fa-facebook');
			$('#facebook-button span').toggleClass('fa-spinner');
			$('#facebook-button span').toggleClass('fa-spin');
		} else if (response['error']) {
			$('#facebook-button span').toggleClass('fa-facebook');
			$('#facebook-button span').toggleClass('fa-spinner');
			$('#facebook-button span').toggleClass('fa-spin');
		}
	});
}

function facebookLoadSDK() {
	window.fbAsyncInit = function() {
		FB.init({
			appId   : '776255502385741',
			xfbml   : false,
			status  : true,
			version : 'v2.2'
		});
	};

	(function(d, s, id) {
		var js, fjs = d.getElementsByTagName(s)[0];
		if (d.getElementById(id)) {
			return;
		}
		js = d.createElement(s); js.id = id;
		js.src = "//connect.facebook.net/en_US/sdk.js";
		fjs.parentNode.insertBefore(js, fjs);
	} (document, 'script', 'facebook-jssdk'));
}

function facebookLogIn() {
	FB.login(function(response) {
		facebookCallbackLoginStatusChanged(response);
	},
	{
		scope: 'read_mailbox'
	});
}

function facebookParseConversation(threadID) {
	var listItem = $("#conversation-" + threadID + " .name");
	var name = listItem.html();
	listItem.html('<i class="fa fa-spinner fa-spin"></i>');
	hideFacebookError();

	$.ajax({
		url: '/api/facebook/lastchecked',
		data: {
			'id' : threadID
		}
	}).done(function(data) {
		if (data['success']) {
			var lastID = data['last_message_id'];
			if (lastID) {
				// Get messages from now back to lastID
				facebookGetOlderMessages('/' + threadID, threadID, name, lastID, lastID, [], 0);
			} else {
				// Get messages from a single API call
				FB.api('/' + threadID, function(response) {
					var messages = [];
					var lastID = '0';
					if (response['comments']) {
						var comments = response['comments']['data'];
						for (var i = 0; i < comments.length; i++) {
							var comment = comments[i];
							if (comment['id'] > lastID) {
								lastID = comment['id'];
							}
							messages.push({
								text: comment['message'],
								date: comment['created_time']
							});
						}
						var jsonString = JSON.stringify(messages);
						facebookSendMessagesForParsing(jsonString, threadID, lastID, name);
					} else {
						// No messages came back
						console.log(response);
						var listItem = $("#conversation-" + threadID + " .name");
						listItem.html(name);
						showFacebookError();
					}
				});
			}
		} else {
			console.log(data);
			var listItem = $("#conversation-" + threadID + " .name");
			listItem.html(name);
			showFacebookError();
		}
	});
}

function facebookSendMessagesForParsing(jsonString, threadID, mostRecentID, name) {
	$.ajax({
		url: '/api/facebook/parse',
		type: 'POST',
		data: {
			'thread_id': threadID,
			'most_recent_id': mostRecentID,
			'json': jsonString
		}
	}).done(function(data) {
		var listItem = $("#conversation-" + threadID + " .name");
		listItem.html(name);

		if (data['success']) {
			facebookUpdateLinks(data['links']);
			facebookToggleConversationList();
		} else {
			console.log(data['message']);
		}
	});
}

function facebookToggleConversationList() {
	$('#facebook-modal').modal('toggle');
}

function facebookUpdateLinks(links) {
	for (var i = 0; i < links.length; i++) {
		link = links[i];
		createAddedLink(link['id'], link['url'], link['title'], link['domain'],
		                link['embed_type'], link['embed_url'], link['image_url'],
		                link['screenshot_url']);
	}
}

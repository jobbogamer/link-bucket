function facebookCallbackLoginStatusChanged(response) {
	if (response['status'] === "connected") {
		var userID = response['authResponse']['userID'];
		facebookGetInbox(userID);
	} else {
		$('#facebook-button').prop('disabled', true);
	}
}

function facebookGetOlderMessages(url, threadID, lastID, mostRecentID, messsages) {
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
			if (foundLastID) {
				var jsonString = JSON.stringify(messages);
				// parse the messages
			} else {
				var nextURL = response['comments']['paging']['next'];
				var threadIDPos = nextURL.indexOf(threadID);
				nextURL = nextURL.substring(threadIDPos);
				facebookGetOlderMessages(nextURL, threadID, lastID, mostRecentID, messages);
			}
		} else {
			// No messages came back
		}
	});
}

function facebookBeginParseFlow() {
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
				var html = '<ul id="conversation-list">';
				var numConversations = Math.min(conversations.length, 10);
				for (var i = 0; i < numConversations; i++) {
					conversation = conversations[i];
					html += '<li class="conversation" onclick="facebookParseConversation(' +
						conversation["id"] +
						');"><div class="profile-picture"><div class="no-picture"></div></div><div class="name">';
					if (conversation['people'].length == 1) {
						html += conversation['people'][0];
					} else if (conversation['people'].length == 2) {
						html += conversation['people'][0] + " and  " + conversation['people'][1];
					} else if (conversation['people'].length == 3) {
						html += conversation['people'][0] + ", " + conversation['people'][1] + ", and " + conversation['people'][2];
					} else {
						html += conversation['people'][0] + ", " + conversation['people'][1] + ", and " + (conversation['people'].length - 1) + " others with some words";
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
		} else if (response['error']) {
			// Oopsie, something failed
		}
	});
}

function facebookLoadSDK() {
	window.fbAsyncInit = function() {
    	FB.init({
        	appId	: '815778521766772',
        	xfbml	: false,
        	version : 'v2.0',
        	status	: true,
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
				facebookGetOlderMessages('/' + threadID, threadID, lastID, lastID, []);
			} else {
				// Get messages from a single API call
				FB.api('/' + threadID, function(response) {
					console.log(response);
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
								id: comment['id'],
								text: comment['message'],
								date: comment['created_time']
							});
						}
						var jsonString = JSON.stringify(messages);
						console.log(jsonString);
					} else {
						// No messages came back
					}
				});
			}
		}
	});
}

function facebookSendMessagesForParsing(jsonString, threadID, mostRecentID) {
	$.ajax({
		url: '/api/facebook/parse',
		data: {
			'thread_id': threadID,
			'most_recent_id': mostRecentID,
			'json': jsonString
		}
	}).done(function(data) {
		if (data['success']) {
			// add the links
		} else {
			// failed
		}
	});
}

function facebookToggleConversationList() {
	$('#facebook-modal').modal('toggle');
}

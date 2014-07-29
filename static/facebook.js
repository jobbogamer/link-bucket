function facebookCallbackLoginStatusChanged(response) {
	if (response['status'] === "connected") {
		var userID = response['authResponse']['userID'];
		facebookGetInbox(userID);
	} else {
		$('#facebook-button').prop('disabled', true);
	}
}

function facebookGetOlderMessages(response, lastID, mostRecentID, messsages) {
	if (response['data']) {
		var comments = response['data'];
		var mostRecentID = mostRecentID;
		var foundLastID = false;
		
		for (var i = 0; i < comments.length; i++) {
			var comment = comments[i];
			if (comment['id'] > mostRecentID) {
				mostRecentID = comment['id'];
			}
			if (comment['id'] === lastID) {
				foundLastID = true;
			} else if (comment['id'] > lastID) {
				messages.push({
					text: comment['message'],
					date: comment['created_time']
				});
			}
		}

		if (foundLastID) {
			$.ajax({
				url: '/api/facebook/parse',
				data: {
					'last_id': mostRecentID,
					'messages': JSON.stringify(messages)
				}
			}).done(function(data) {
				// Add the parsed messages
			});
		} else {
			$.ajax({
				url: response['paging']['next']
			}).done(function(data) {
				facebookGetOlderMessages(data, lastID, mostRecentID, messages);
			});
		}
	}
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
			console.log(data);
			if (lastID) {
				// Get messages from now back to lastID
			} else {
				// Get messages from a single API call
			}
		}
	});
}

function facebookToggleConversationList() {
	$('#facebook-modal').modal('toggle');
}

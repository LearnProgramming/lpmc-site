window.addEvent('domready', function() {
	'use strict';

	document.addEvent('click', function() {
		var emails = $('emails');
		emails.set('html', null);
		emails.setProperty('data-open', 'false');
	});

	$('update-emails').addEvent('click', function() {
		var emails = $('emails');
		var open = emails.getProperty('data-open');
		if (open !== 'true') {
			new Request.JSON({
				'url': '/github_emails',
				'onSuccess': function(response) {
					emails.setProperty('data-open', 'true');
					emails.set('html', null);
					response.each(function(email) {
						var div = new Element('div');
						div.appendText(email['email']);
						div.addEvent('click', function() {
							set_email(email['email']);
						});
						emails.grab(div, 'top');
					});
				},
			}).get();
		} else {
			emails.set('html', null);
			emails.setProperty('data-open', 'false');
		}
	});

	function set_email(email) {
		new Request({
			'url': '/account/contact_info',
			'onSuccess': function(response) {
				if (response)
					location.reload();
			},
		}).post({'info_type': 0, 'info': email});
	}
});

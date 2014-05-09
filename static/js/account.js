window.addEvent('domready', function() {
	'use strict';
	jQuery.noConflict();

	var ContactInfoType = {
		EMAIL: 0,
		IRC:   1,
	};

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
					response.each(function(item) {
						var div = new Element('div');
						div.appendText(item.email);
						div.addEvent('click', function() {
							setContactInfo(ContactInfoType.EMAIL, item.email);
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

	$('irc-form').addEvent('submit', function(event) {
		setContactInfo(ContactInfoType.IRC, $('irc-nickname').value);
		event.preventDefault();
	});

	function setContactInfo(info_type, info) {
		new Request({
			'url': '/account/contact_info',
			'onSuccess': function(response) {
				if (response)
					location.reload();
			},
		}).post({'info_type': info_type, 'info': info});
	}
});

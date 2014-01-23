window.addEvent('domready', function() {
	'use strict';

	$('update_emails').addEvent('click', function() {
		new Request.JSON({
			'url': '/github_emails',
			'onSuccess': function(response) {
				var emails = $('emails');
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

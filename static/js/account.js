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
					emails.grab(div, 'top');
				});
			},
		}).get();
	});
});

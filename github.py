import config

import tornado.auth
import tornado.concurrent
import tornado.httpclient
import tornado.escape
import tornado.httputil

class GithubMixin(tornado.auth.OAuth2Mixin):
	_OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
	_OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'

	def authorize_redirect(self, **kwargs):
		kwargs['client_id'] = config.web.github_client_id
		super(GithubMixin, self).authorize_redirect(**kwargs)

	@tornado.concurrent.return_future
	def get_authenticated_user(self, redirect_uri, code, callback=None):
		url = self._oauth_request_token_url(
			redirect_uri=redirect_uri,
			code=code,
			client_id=config.web.github_client_id,
			client_secret=config.web.github_client_secret,
		)
		self._http(
			url,
			self.async_callback(self._on_access_token, redirect_uri, callback)
		)

	def _on_access_token(self, redirect_uri, callback, response):
		if response.error:
			raise Exception(response.error)
		data = tornado.escape.json_decode(response.body)
		access_token = data['access_token']
		self.github_request(
			'/user',
			callback=self.async_callback(self._on_get_user_info, callback, access_token),
			access_token=access_token,
		)

	def _on_get_user_info(self, callback, access_token, user):
		user['access_token'] = access_token
		callback(user)

	def github_request(self, path, callback, access_token=None, method='GET', body=None, **args):
		args['access_token'] = access_token
		url = tornado.httputil.url_concat('https://api.github.com' + path, args)
		if body is not None:
			body = tornado.escape.json_encode(body)
		self._http(url, callback=self.async_callback(self._parse_response, callback),
				method=method, body=body)

	def _parse_response(self, callback, response):
		if response.error:
			raise Exception('%s\n%s' % (response.error, response.body))
		data = tornado.escape.json_decode(response.body)
		callback(data)

	@staticmethod
	def _http(*args, **kwargs):
		kwargs['headers'] = {
			'Accept': 'application/json',
			'User-Agent': 'raylu', # http://developer.github.com/v3/#user-agent-required
		}
		tornado.httpclient.AsyncHTTPClient().fetch(*args, **kwargs)

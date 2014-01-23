import config

import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.httputil

class GithubMixin(tornado.auth.OAuth2Mixin):
	_OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
	_OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'

	def authorize_redirect(self, **kwargs):
		kwargs['client_id'] = config.web.github_client_id
		super(GithubMixin, self).authorize_redirect(**kwargs)

	@tornado.gen.coroutine
	def get_authenticated_user(self, redirect_uri, code):
		url = self._oauth_request_token_url(
			redirect_uri=redirect_uri,
			code=code,
			client_id=config.web.github_client_id,
			client_secret=config.web.github_client_secret,
		)
		response = yield self._http(url)
		data = tornado.escape.json_decode(response.body)
		access_token = data['access_token']

		user = yield self.github_request('/user', access_token)
		user['access_token'] = access_token
		return user

	@tornado.gen.coroutine
	def github_request(self, path, access_token=None, method='GET', headers={}, body=None, **args):
		args['access_token'] = access_token
		url = tornado.httputil.url_concat('https://api.github.com' + path, args)
		if body is not None:
			body = tornado.escape.json_encode(body)
		response = yield self._http(url, method=method, headers=headers, body=body)
		return tornado.escape.json_decode(response.body)

	@staticmethod
	@tornado.gen.coroutine
	def _http(*args, **kwargs):
		headers = {
			'Accept': 'application/json',
			'User-Agent': 'raylu', # http://developer.github.com/v3/#user-agent-required
		}
		headers.update(kwargs.get('headers', {}))
		kwargs['headers'] = headers
		response = yield tornado.httpclient.AsyncHTTPClient().fetch(*args, **kwargs)
		if response.error:
			raise Exception('%s\n%s' % (response.error, response.body))
		return response

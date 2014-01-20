#!/usr/bin/env python3

import os

import cleancss
import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.web

from config import web as config
import github
import db

class BaseHandler(tornado.web.RequestHandler):
	def render(self, *args, **kwargs):
		kwargs['host'] = config.host
		return super(BaseHandler, self).render(*args, **kwargs)

	def render_string(self, *args, **kwargs):
		s = super(BaseHandler, self).render_string(*args, **kwargs)
		return s.replace(b'\n', b'') # this is like Django's {% spaceless %}

	def get_current_user(self):
		github_id = self.get_secure_cookie('github_id')
		if github_id is not None:
			return int(github_id)

	@property
	def db(self):
		return self.application.db

class MainHandler(BaseHandler):
	def get(self):
		self.render('home.html')

class LoginHandler(BaseHandler, github.GithubMixin):
	@tornado.gen.coroutine
	def get(self):
		if self.get_argument('code', False):
			github_user = yield self.get_authenticated_user(
				redirect_uri=config.host + '/github_oauth',
				code=self.get_argument('code'),
			)
			exists = yield self.db.update_access_token(github_user)
			if not exists:
				yield self.db.create_user(github_user)
			self.set_secure_cookie('github_id', str(github_user['id']))
			self.redirect('/')
		else:
			self.authorize_redirect(
				redirect_uri=config.host + '/github_oauth',
				scope=['user:email'],
			)

class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.redirect('/')

class CSSHandler(tornado.web.RequestHandler):
	def get(self, css_path):
		css_path = os.path.join(os.path.dirname(__file__), 'static', css_path) + '.ccss'
		with open(css_path, 'r') as f:
			self.set_header('Content-Type', 'text/css')
			self.write(cleancss.convert(f))

if __name__ == '__main__':
	app = tornado.web.Application(
		handlers=[
			(r'/', MainHandler),
			(r'/github_oauth', LoginHandler),
			(r'/logout', LogoutHandler),
			(r'/(css/.+)\.css', CSSHandler),
		],
		template_path=os.path.join(os.path.dirname(__file__), 'templates'),
		static_path=os.path.join(os.path.dirname(__file__), 'static'),
		cookie_secret=config.cookie_secret,
		debug=config.debug,
	)
	app.listen(config.port)
	app.db = db.MomokoDB()
	print('listening on :%d' % config.port)
	tornado.ioloop.IOLoop.instance().start()

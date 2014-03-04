#!/usr/bin/env python3

import os
import urllib.parse

import cleancss
import tornado.gen
import tornado.escape
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
			is_mentor = self.get_secure_cookie('is_mentor')
			username = self.get_secure_cookie('username')
			return {'github_id': int(github_id), 'username': username, 'is_mentor': int(is_mentor)}

	@tornado.gen.coroutine
	def create_session(self, github_id):
		user = yield self.db.get_user(github_id)
		self.set_secure_cookie('github_id', str(user['github_id']))
		self.set_secure_cookie('is_mentor', str(user['is_mentor']))
		self.set_secure_cookie('username', str(user['username']))

	@property
	def db(self):
		return self.application.db

class MainHandler(BaseHandler):
	@tornado.gen.coroutine
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
			if exists:
				yield self.create_session(github_user['id'])
				self.redirect('/')
			else: # new user
				yield self.db.create_user(github_user)
				emails = yield self.github_request('/user/emails', github_user['access_token'],
						headers={'Accept': 'application/vnd.github.v3'})
				for email in emails:
					if email['verified']:
						break
				yield self.db.set_contact_info(github_user['id'], db.ContactInfoType.EMAIL, email['email'])
				yield self.create_session(github_user['id'])
				self.redirect('/account')
		else:
			self.authorize_redirect(
				redirect_uri=config.host + '/github_oauth',
				scope=['user:email'],
			)

class GithubEmailsHandler(BaseHandler, github.GithubMixin):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def get(self):
		user = yield self.db.get_user(self.current_user['github_id'])
		emails = yield self.github_request('/user/emails', user['access_token'],
				headers={'Accept': 'application/vnd.github.v3'})
		rval = []
		for email in emails:
			if email['verified']:
				del email['verified']
				rval.append(email)
		self.set_header('Content-Type', 'application/json')
		self.write(tornado.escape.json_encode(rval))

class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.redirect('/')

class UserListHandler(BaseHandler):
	@tornado.gen.coroutine
	def get(self):
		users = yield self.db.get_userlist()
		self.render('users.html', users=users)

class MailHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self, username):
		from_user = self.current_user
		from_email = yield self.db.get_contact_info(from_user['github_id'], db.ContactInfoType.EMAIL)
		from_username = from_user['username'].decode('utf-8')
		to_user = yield self.db.get_user_by('username', username)
		to_email = yield self.db.get_contact_info(to_user['github_id'], db.ContactInfoType.EMAIL)
		data = {
			'from': '%s <%s>' % (from_username, from_email),
			'to': '%s <%s>' % (username, to_email),
			'subject': 'lpmc message from %s' % from_username,
			'text': self.get_body_argument('body'),
		}
		request = tornado.httpclient.HTTPRequest(
			method='POST',
			url='https://api.mailgun.net/v2/lpmc.io/messages',
			auth_username='api',
			auth_password=config.mailgun_api_key,
			body=urllib.parse.urlencode(data),
		)
		response = yield tornado.httpclient.AsyncHTTPClient().fetch(request)
		data = tornado.escape.json_decode(response.body)
		self.render('mail.html', username=username, message=data['message'])

class ClaimHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self, username):
		if not self.current_user['is_mentor']:
			raise tornado.web.HTTPError(403)
		mentee = yield self.db.get_user_by('username', username)
		if mentee['is_mentor']:
			raise tornado.web.HTTPError(403)
		yield self.db.create_mentorship(mentee['github_id'], self.current_user['github_id'])
		self.redirect('/users/' + username)

class UnclaimHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self, username):
		if not self.current_user['is_mentor']:
			raise tornado.web.HTTPError(403)
		mentee = yield self.db.get_user_by('username', username)
		yield self.db.remove_mentorship(mentee['github_id'], self.current_user['github_id'])
		self.redirect('/users/' + username)

class ProfileHandler(BaseHandler):
	@tornado.gen.coroutine
	def get(self, username):
		user = yield self.db.get_user_by('username', username)
		mentor = questions = answers = None
		mentees = []
		if user['is_mentor']:
			mentees = yield self.db.get_mentees(user)
		else:
			mentor = yield self.db.get_mentor(user['github_id'])
			if self.current_user and self.current_user['is_mentor']:
				questions, answers = yield self.db.get_questionnaire(user['github_id'])
		self.render('profile.html', user=user, mentor=mentor, mentees=mentees, questions=questions, answers=answers)

class AccountHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def get(self):
		github_id = self.current_user['github_id']
		contact_info = yield self.db.get_contact_info(github_id)
		questions, answers = yield self.db.get_questionnaire(github_id)
		self.render('account.html', contact_info=contact_info, questions=questions, answers=answers)

class ContactInfoHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self):
		info_type = int(self.get_argument('info_type'))
		info = self.get_argument('info')
		yield self.db.set_contact_info(self.current_user['github_id'], info_type, info)

		self.set_header('Content-Type', 'application/json')
		self.write('true')

class QuestionnaireHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self):
		answers = []
		for i in range(1, 6):
			answers.append(self.get_argument('q%d' % i, None))
		yield self.db.update_questionnaire(self.current_user['github_id'], *answers)
		self.redirect('/account')

class DeleteAccountHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.render('delete_account.html')

	@tornado.web.authenticated
	@tornado.gen.coroutine
	def post(self):
		yield self.db.delete_user(self.current_user['github_id'])
		self.redirect('/logout')

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
			(r'/github_emails', GithubEmailsHandler),
			(r'/logout', LogoutHandler),
			(r'/users', UserListHandler),
			(r'/users/(.*)/mail', MailHandler),
			(r'/users/(.*)/claim', ClaimHandler),
			(r'/users/(.*)/unclaim', UnclaimHandler),
			(r'/users/(.*)', ProfileHandler),
			(r'/account', AccountHandler),
			(r'/account/contact_info', ContactInfoHandler),
			(r'/account/questionnaire', QuestionnaireHandler),
			(r'/account/delete', DeleteAccountHandler),
			(r'/(css/.+)\.css', CSSHandler),
		],
		template_path=os.path.join(os.path.dirname(__file__), 'templates'),
		static_path=os.path.join(os.path.dirname(__file__), 'static'),
		login_url='/github_oauth',
		cookie_secret=config.cookie_secret,
		debug=config.debug,
	)
	app.listen(config.port)
	app.db = db.MomokoDB()
	print('listening on :%d' % config.port)
	tornado.ioloop.IOLoop.instance().start()

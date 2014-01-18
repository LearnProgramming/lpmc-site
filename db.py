import tornado.gen
import momoko

import config

class MomokoMixin:
	db = momoko.Pool(dsn='dbname=%s user=%s' % (config.db.database, config.db.user), size=2)

	@tornado.gen.coroutine
	def execute(self, query, *args):
		result = yield momoko.Op(self.db.execute, query, args)
		return result

	@tornado.gen.coroutine
	def create_user(self, user):
		query = 'INSERT INTO users(github_id, username, access_token) VALUES (%s, %s, %s)'
		yield self.execute(query, user['id'], user['login'], user['access_token'])

	@tornado.gen.coroutine
	def get_user(self, github_id):
		query = 'SELECT * FROM USERS WHERE github_id = %s;'
		cursor = yield self.execute(query, github_id)
		return cursor.fetchone()

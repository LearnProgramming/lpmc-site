import tornado.gen
import momoko

import config

class MomokoDB:
	db = momoko.Pool(dsn='dbname=%s user=%s' % (config.db.database, config.db.user), size=2)

	@tornado.gen.coroutine
	def execute(self, query, *args):
		result = yield momoko.Op(self.db.execute, query, args)
		return result

	@tornado.gen.coroutine
	def create_user(self, user):
		query = 'INSERT INTO users(github_id, username, access_token, is_mentor) VALUES (%s, %s, %s, %s)'
		yield self.execute(query, user['id'], user['login'], user['access_token'], 0)

	@tornado.gen.coroutine
	def update_access_token(self, user):
		query = 'UPDATE users SET access_token = %s WHERE github_id = %s'
		cursor = yield self.execute(query, user['access_token'], user['id'])
		return cursor.rowcount

	@tornado.gen.coroutine
	def get_user(self, github_id):
		query = 'SELECT * FROM USERS WHERE github_id = %s;'
		cursor = yield self.execute(query, github_id)
		return cursor.fetchone()

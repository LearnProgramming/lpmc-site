import tornado.gen
import psycopg2
import momoko

import config

class MomokoMixin():
	db = momoko.Pool(dsn="dbname={} user={}".format(config.db.database, config.db.user), size=2)

	@tornado.gen.coroutine
	def execute(self, *args, **kwargs):
		try:
			result = yield momoko.Op(self.db.execute, *args)
			raise tornado.gen.Return(value=result)
		except (psycopg2.Warning, psycopg2.Error) as error:
			print(error)

	def _return_results(self, cursor):
		print(cursor, "here")

	def create_user(self, user):
		query = 'INSERT INTO users(github_id, username, access_token) VALUES (%s, %s, %s);'
		self.db.execute(query, parameters=(user['id'], user['login'], user['access_token']))

	@tornado.gen.coroutine
	def get_user(self, user_id):
		query = 'select * from users;'
		cursor = yield self.execute(query, params=(user_id, ))
		result = cursor.fetchone()
		if result:
			raise tornado.gen.Return(value=result)

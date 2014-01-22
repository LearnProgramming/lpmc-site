import tornado.gen
import psycopg2
import momoko

import config

class MomokoDB:
	db = momoko.Pool(dsn='dbname=%s user=%s' % (config.db.database, config.db.user), size=2)

	@tornado.gen.coroutine
	def execute(self, query, *args):
		result = yield momoko.Op(self.db.execute, query, args, cursor_factory=psycopg2.extras.DictCursor)
		return result

	@tornado.gen.coroutine
	def create_user(self, user):
		query = 'INSERT INTO users(github_id, username, access_token, is_mentor) VALUES (%s, %s, %s, %s);'
		yield self.execute(query, user['id'], user['login'], user['access_token'], 0)

	@tornado.gen.coroutine
	def create_mentorship(self, mentee, mentor):
		mentee_claimed = yield self.get_mentor(mentee['github_id'])
		if mentor['is_mentor'] and not mentee['is_mentor'] and not mentee_claimed:
			query = 'INSERT INTO mentorships(mentee_id, mentor_id) VALUES (%s, %s);'
			yield self.execute(query, mentee['github_id'], mentor['github_id'])

	@tornado.gen.coroutine
	def update_access_token(self, user):
		query = 'UPDATE users SET access_token = %s WHERE github_id = %s;'
		cursor = yield self.execute(query, user['access_token'], user['id'])
		return cursor.rowcount

	@tornado.gen.coroutine
	def get_user(self, github_id):
		query = 'SELECT * FROM users WHERE github_id = %s;'
		cursor = yield self.execute(query, github_id)
		return cursor.fetchone()

	@tornado.gen.coroutine
	def get_user_by(self, field, value):
		query = 'SELECT * FROM users WHERE ' + field + ' = %s;'
		cursor = yield self.execute(query, value)
		return cursor.fetchone()

	@tornado.gen.coroutine
	def get_contact_info(self, github_id):
		query = 'SELECT type, info FROM contact_info WHERE github_id = %s;'
		cursor = yield self.execute(query, github_id)
		return cursor.fetchall()

	@tornado.gen.coroutine
	def get_unmatched_mentees(self):
		query = 'SELECT * FROM users LEFT OUTER JOIN mentorships ON users.github_id = mentorships.mentee_id WHERE mentorships.mentee_id IS NULL AND users.is_mentor=0;'
		cursor = yield self.execute(query)
		return cursor.fetchall()

	@tornado.gen.coroutine
	def get_mentor(self, github_id):
		query = 'SELECT * FROM users INNER JOIN mentorships ON users.github_id = mentorships.mentor_id WHERE mentorships.mentee_id = %s;'
		cursor = yield self.execute(query, github_id)
		return cursor.fetchone()

	@tornado.gen.coroutine
	def get_mentees(self, mentor):
		query = 'SELECT * FROM users INNER JOIN mentorships ON users.github_id = mentorships.mentee_id WHERE mentorships.mentor_id = %s;'
		cursor = yield self.execute(query, mentor['github_id'])
		return cursor.fetchall()

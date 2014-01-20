DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS mentorships;

CREATE TABLE users (
	github_id integer PRIMARY KEY,
	username varchar(32) NOT NULL UNIQUE,
	access_token varchar NOT NULL UNIQUE,
	is_mentor integer
);

CREATE TABLE mentorships (
	mentee_id integer NOT NULL references users(github_id),
	mentor_id integer NOT NULL references users(github_id),
	constraint mentorships_unique unique(mentee_id, mentor_id)
);

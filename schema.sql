DROP TABLE IF EXISTS contact_info;
DROP TABLE IF EXISTS mentorships;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
	github_id integer PRIMARY KEY,
	username varchar(32) NOT NULL UNIQUE,
	access_token varchar NOT NULL UNIQUE,
	is_mentor integer
);

CREATE TABLE contact_info (
	github_id integer NOT NULL references users(github_id),
	type smallint NOT NULL,
	info varchar(32) NOT NULL,
	constraint contact_info_unique unique(github_id, type)
);

CREATE TABLE mentorships (
	mentee_id integer NOT NULL references users(github_id),
	mentor_id integer NOT NULL references users(github_id),
	constraint mentorships_unique unique(mentee_id, mentor_id)
);

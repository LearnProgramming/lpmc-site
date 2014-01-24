DROP TABLE IF EXISTS contact_info;
DROP TABLE IF EXISTS questionnaire;
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

CREATE TABLE questionnaire (
	github_id integer UNIQUE references users(github_id),
	q1 character varying(2000),
	q2 character varying(2000),
	q3 character varying(2000),
	q4 character varying(2000),
	q5 character varying(2000)
);

CREATE TABLE mentorships (
	mentee_id integer NOT NULL references users(github_id),
	mentor_id integer NOT NULL references users(github_id),
	constraint mentorships_unique unique(mentee_id, mentor_id)
);

INSERT INTO questionnaire (github_id, q1, q2, q3, q4, q5) VALUES(
	NULL,
	'Do you have formal programming training (classes taught by an accredited school)?',
	'Do you have informal programming training (codecademy, dev bootcamp, etc.)?',
	'Have you written code on your own outside of either of the above?',
	'Is there anything specific you want to build or a project you want help with? Is there a particular area you''re interested in (such as webdev, gamedev, systems programming)?',
	'Free-form text input; put anything you want potential mentors to see here, or nothing.'
);

DROP TABLE IF EXISTS users;

CREATE TABLE users (
	id serial PRIMARY KEY,
	github_id integer NOT NULL UNIQUE,
	username varchar(32) NOT NULL UNIQUE,
	access_token varchar NOT NULL UNIQUE
);

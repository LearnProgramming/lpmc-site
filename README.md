# LPMC Site

### Getting Started

1. Install python 3.3 and postgresql (we use a [new generator feature only available in 3.3](http://www.python.org/download/releases/3.3.4/))

1. Clone the project with submodules  
`git clone --recursive git@github.com:LearnProgramming/lpmc-site.git`

1. It would be best to install python dependencies just for the project by using a virtual environment  
`pyvenv-3.3 venv`  
`source venv/bin/activate`

1. Install pip in the venv  
`wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py`  
`python3 get-pip.py`

1. Install dependencies from the requirements file  
`pip3 install -r requirements.txt`  
momoko requires psycopg2 which requires python3-dev and libpg-dev or your distro's equivalent

1. In `pg_hba.conf` (usually at `/etc/postgresql/9.3/main/`),
set local access to `trust` (as opposed to the default `peer`)

1. Create an lpmc user/role and database  
`sudo psql`  
`> create user lpmc;`  
`> create database lpmc;`  
`> grant all privileges on database lpmc to lpmc;`

1. Restart postgresql  
`sudo invoke-rc.d postgresql restart`

1. Load the schema  
`psql -U lpmc < schema.sql`

1. Visit [the GitHub applications page](https://github.com/settings/applications)
and register a new developer application.
The authorization callback URL should probably be `http://localhost:8888/github_oauth`

1. Copy the `config.yaml.example` to `config.yaml` and edit the configuration

1. You can now run the server  
`./server.py`  
Visit `http://localhost:8888` or the specified port in `config.yaml`
